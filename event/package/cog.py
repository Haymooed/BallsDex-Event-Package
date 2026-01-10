from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Iterable, Sequence

import discord
from asgiref.sync import sync_to_async
from discord import app_commands
from discord.ext import commands
from django.db import transaction
from django.utils import timezone

from bd_models.models import BallInstance, Player
from ..models import (
    CraftingIngredient,
    CraftingItem,
    CraftingLog,
    CraftingProfile,
    CraftingRecipe,
    CraftingRecipeState,
    CraftingSettings,
    PlayerItemBalance,
)

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

Interaction = discord.Interaction["BallsDexBot"]


def format_seconds(seconds: float) -> str:
    """Format seconds as a human friendly string."""
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


async def get_settings() -> CraftingSettings:
    """Load crafting settings in async context."""
    return await sync_to_async(CraftingSettings.get_solo)()


async def ensure_player(user: discord.abc.User) -> Player:
    """Ensure a Player row exists for a Discord user."""
    player, _ = await Player.objects.aget_or_create(discord_id=user.id)
    return player


async def ensure_profile(player: Player) -> CraftingProfile:
    profile, _ = await CraftingProfile.objects.aget_or_create(player=player)
    return profile


async def ensure_state(player: Player, recipe: CraftingRecipe) -> CraftingRecipeState:
    state, _ = await CraftingRecipeState.objects.aget_or_create(player=player, recipe=recipe)
    return state


async def recipe_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete enabled recipe names."""
    recipes = CraftingRecipe.objects.filter(enabled=True).order_by("name")
    recipe_names = await sync_to_async(list)(recipes.values_list("name", flat=True))
    if current:
        recipe_names = [name for name in recipe_names if current.lower() in name.lower()]
    return [app_commands.Choice(name=name, value=name) for name in recipe_names[:25]]


def ingredient_summary(ingredient: CraftingIngredient) -> str:
    """Readable description for an ingredient."""
    target = ingredient.ball or ingredient.item
    return f"{ingredient.quantity} × {target} ({ingredient.get_ingredient_type_display()})"


@dataclass
class CraftOutcome:
    success: bool
    message: str
    next_retry_after: float | None = None
    result_summary: str | None = None


class CraftingCog(commands.GroupCog, name="craft"):
    """Craft collectibles through admin-defined recipes."""

    def __init__(self, bot: "BallsDexBot"):
        super().__init__()
        self.bot = bot

    @property
    def qualified_name(self) -> str:
        return "craft"

    # ----- Internal helpers -----

    async def _get_recipe(self, name: str) -> CraftingRecipe | None:
        try:
            return await CraftingRecipe.objects.aget(name__iexact=name)
        except CraftingRecipe.DoesNotExist:
            return None

    async def _collect_ingredients(self, recipe: CraftingRecipe) -> list[CraftingIngredient]:
        return await sync_to_async(list)(
            recipe.ingredients.select_related("ball", "item").all()
        )

    async def _check_cooldowns(
        self,
        settings: CraftingSettings,
        profile: CraftingProfile,
        state: CraftingRecipeState,
    ) -> tuple[bool, float]:
        now = timezone.now()
        remaining: float = 0
        if settings.global_cooldown_seconds and profile.last_crafted_at:
            delta = (profile.last_crafted_at + timedelta(seconds=settings.global_cooldown_seconds) - now).total_seconds()
            remaining = max(remaining, delta)
        if state.last_crafted_at and state.recipe.cooldown_seconds:
            delta = (state.last_crafted_at + timedelta(seconds=state.recipe.cooldown_seconds) - now).total_seconds()
            remaining = max(remaining, delta)
        return remaining <= 0, max(0, remaining)

    async def _check_requirements(
        self, player: Player, ingredients: Sequence[CraftingIngredient]
    ) -> tuple[bool, str]:
        """Validate ingredient availability without consuming."""
        for ingredient in ingredients:
            if ingredient.ingredient_type == CraftingIngredient.INGREDIENT_BALL:
                qs = BallInstance.objects.filter(
                    player=player, ball=ingredient.ball, deleted=False
                )
                owned = await qs.acount()
                if owned < ingredient.quantity:
                    return False, f"You need {ingredient.quantity} × {ingredient.ball} (you have {owned})."
            elif ingredient.ingredient_type == CraftingIngredient.INGREDIENT_ITEM:
                balance, _ = await PlayerItemBalance.objects.aget_or_create(
                    player=player, item=ingredient.item, defaults={"quantity": 0}
                )
                if balance.quantity < ingredient.quantity:
                    return False, f"You need {ingredient.quantity} × {ingredient.item} (you have {balance.quantity})."
        return True, ""

    async def _consume_ingredients(self, player: Player, ingredients: Sequence[CraftingIngredient]) -> None:
        """Consume balls/items after validation."""
        for ingredient in ingredients:
            if ingredient.ingredient_type == CraftingIngredient.INGREDIENT_BALL and ingredient.ball:
                qs = BallInstance.objects.filter(
                    player=player, ball=ingredient.ball, deleted=False
                ).order_by("catch_date")
                ids = await sync_to_async(list)(qs.values_list("id", flat=True)[: ingredient.quantity])
                if len(ids) < ingredient.quantity:
                    raise RuntimeError("Insufficient ball instances during consumption.")
                await BallInstance.objects.filter(id__in=ids).aupdate(deleted=True)
            elif ingredient.ingredient_type == CraftingIngredient.INGREDIENT_ITEM and ingredient.item:
                balance, _ = await PlayerItemBalance.objects.aget_or_create(
                    player=player, item=ingredient.item, defaults={"quantity": 0}
                )
                if balance.quantity < ingredient.quantity:
                    raise RuntimeError("Insufficient item balance during consumption.")
                balance.quantity -= ingredient.quantity
                await balance.asave(update_fields=("quantity",))

    async def _grant_result(self, player: Player, recipe: CraftingRecipe) -> str:
        """Grant crafted reward."""
        if recipe.result_type == CraftingRecipe.RESULT_ITEM and recipe.result_item:
            balance, _ = await PlayerItemBalance.objects.aget_or_create(
                player=player, item=recipe.result_item, defaults={"quantity": 0}
            )
            balance.quantity += recipe.result_quantity
            await balance.asave(update_fields=("quantity",))
            return f"Received {recipe.result_quantity} × {recipe.result_item.name}."

        # Default to ball instance creation
        ball = recipe.result_ball
        if not ball:
            raise RuntimeError("Recipe missing ball result.")

        created_ids: list[int] = []
        for _ in range(recipe.result_quantity):
            new_instance = await BallInstance.objects.acreate(
                ball=ball,
                player=player,
                special=recipe.result_special,
                attack_bonus=0,
                health_bonus=0,
                spawned_time=timezone.now(),
                catch_date=timezone.now(),
            )
            created_ids.append(new_instance.pk)

        ids_display = ", ".join(f"#{pk:0X}" for pk in created_ids)
        special_suffix = f" with {recipe.result_special}" if recipe.result_special else ""
        return f"Crafted {recipe.result_quantity} × {ball.country}{special_suffix} ({ids_display})."

    async def _log_attempt(self, player: Player, recipe: CraftingRecipe, outcome: CraftOutcome) -> None:
        await CraftingLog.objects.acreate(
            player=player,
            recipe=recipe,
            success=outcome.success,
            message=outcome.message,
        )

    async def _perform_craft(
        self, player: Player, recipe: CraftingRecipe, *, allow_auto: bool = False
    ) -> CraftOutcome:
        """Execute a craft attempt including validation and consumption."""
        settings = await get_settings()
        if not settings.enabled:
            return CraftOutcome(False, "Crafting is currently disabled by admins.")
        if not recipe.enabled:
            return CraftOutcome(False, "That recipe is disabled.")
        if allow_auto:
            if not settings.allow_auto_crafting:
                return CraftOutcome(False, "Auto-crafting is disabled by admins.")
            if not recipe.allow_auto:
                return CraftOutcome(False, "Auto-crafting is disabled for this recipe.")

        profile = await ensure_profile(player)
        state = await ensure_state(player, recipe)
        ready, remaining = await self._check_cooldowns(settings, profile, state)
        if not ready:
            return CraftOutcome(
                False,
                f"Recipe is on cooldown. Try again in {format_seconds(remaining)}.",
                next_retry_after=remaining,
            )

        ingredients = await self._collect_ingredients(recipe)
        ok, reason = await self._check_requirements(player, ingredients)
        if not ok:
            return CraftOutcome(False, reason)

        async with transaction.atomic():
            await self._consume_ingredients(player, ingredients)
            result = await self._grant_result(player, recipe)
            state.update_cooldown()
            profile.update_cooldown()
            await state.asave(update_fields=("last_crafted_at",))
            await profile.asave(update_fields=("last_crafted_at",))
        return CraftOutcome(True, "Craft successful!", result_summary=result)

    def _recipe_embed(
        self, recipe: CraftingRecipe, ingredients: Sequence[CraftingIngredient] | None = None
    ) -> discord.Embed:
        embed = discord.Embed(title=recipe.name, description=recipe.description or "No description provided.")
        ingredient_list = ingredients if ingredients is not None else recipe.ingredients.all()
        ingredients_text = "\n".join(ingredient_summary(i) for i in ingredient_list) or "None"
        embed.add_field(name="Ingredients", value=ingredients_text, inline=False)
        if recipe.result_type == CraftingRecipe.RESULT_ITEM:
            result = f"{recipe.result_quantity} × {recipe.result_item}"
        else:
            special = f" with {recipe.result_special}" if recipe.result_special else ""
            result = f"{recipe.result_quantity} × {recipe.result_ball}{special}"
        embed.add_field(name="Result", value=result, inline=False)
        cooldown_text = format_seconds(recipe.cooldown_seconds) if recipe.cooldown_seconds else "None"
        embed.add_field(name="Recipe Cooldown", value=cooldown_text, inline=True)
        embed.add_field(name="Auto-Crafting", value="Enabled" if recipe.allow_auto else "Disabled", inline=True)
        return embed

    # ----- Commands -----

    @app_commands.command(name="view", description="View all available crafting recipes.")
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def craft_view(self, interaction: Interaction):
        settings = await get_settings()
        if not settings.enabled:
            await interaction.response.send_message("Crafting is currently disabled.", ephemeral=True)
            return

        recipes = await sync_to_async(list)(
            CraftingRecipe.objects.filter(enabled=True).prefetch_related("ingredients", "ingredients__ball", "ingredients__item")
        )
        if not recipes:
            await interaction.response.send_message("No crafting recipes are available right now.", ephemeral=True)
            return

        embeds = [self._recipe_embed(recipe, list(recipe.ingredients.all())) for recipe in recipes][:10]
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

    @app_commands.command(name="craft", description="Craft a recipe if requirements are met.")
    @app_commands.describe(recipe="Recipe name to craft")
    @app_commands.autocomplete(recipe=recipe_autocomplete)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def craft(self, interaction: Interaction, recipe: str):
        await interaction.response.defer(thinking=True)
        recipe_obj = await self._get_recipe(recipe)
        if not recipe_obj:
            await interaction.followup.send(f"Recipe '{recipe}' was not found.", ephemeral=True)
            return

        player = await ensure_player(interaction.user)
        outcome = await self._perform_craft(player, recipe_obj, allow_auto=False)
        await self._log_attempt(player, recipe_obj, outcome)

        if outcome.success:
            ingredients = await self._collect_ingredients(recipe_obj)
            embed = self._recipe_embed(recipe_obj, ingredients)
            embed.color = discord.Color.green()
            embed.add_field(name="Result", value=outcome.result_summary or "Crafted!", inline=False)
            await interaction.followup.send(f"✅ {outcome.message}", embed=embed)
        else:
            await interaction.followup.send(f"❌ {outcome.message}", ephemeral=True)

    @app_commands.command(
        name="auto",
        description="Automatically craft a recipe whenever possible until disabled.",
    )
    @app_commands.describe(recipe="Recipe to auto-craft (use 'off' or '0' to disable)")
    @app_commands.autocomplete(recipe=recipe_autocomplete)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def craft_auto(self, interaction: Interaction, recipe: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        player = await ensure_player(interaction.user)
        settings = await get_settings()

        if recipe.lower() in {"off", "stop", "0"}:
            updated = await CraftingRecipeState.objects.filter(player=player, auto_enabled=True).aupdate(auto_enabled=False)
            await interaction.followup.send(f"Auto-crafting disabled for {updated} recipe(s).", ephemeral=True)
            return

        if not settings.allow_auto_crafting:
            await interaction.followup.send("Auto-crafting is disabled by admins.", ephemeral=True)
            return

        recipe_obj = await self._get_recipe(recipe)
        if not recipe_obj:
            await interaction.followup.send(f"Recipe '{recipe}' was not found.", ephemeral=True)
            return
        if not recipe_obj.allow_auto:
            await interaction.followup.send("Auto-crafting is disabled for this recipe.", ephemeral=True)
            return

        state = await ensure_state(player, recipe_obj)
        state.auto_enabled = True
        await state.asave(update_fields=("auto_enabled",))

        # Attempt to craft in a bounded loop respecting cooldowns.
        crafted = 0
        outcome: CraftOutcome | None = None
        for _ in range(5):  # avoid infinite loops
            outcome = await self._perform_craft(player, recipe_obj, allow_auto=True)
            await self._log_attempt(player, recipe_obj, outcome)
            if not outcome.success:
                if outcome.next_retry_after and outcome.next_retry_after <= 30:
                    await asyncio.sleep(outcome.next_retry_after)
                    continue
                break
            crafted += 1

        if outcome and outcome.success:
            msg = f"Auto-crafted {crafted} time(s). Last result: {outcome.result_summary}"
            await interaction.followup.send(msg, ephemeral=True)
        elif outcome:
            await interaction.followup.send(
                f"Auto-crafting stopped: {outcome.message} (crafted {crafted} time(s)).", ephemeral=True
            )
        else:
            await interaction.followup.send("Auto-crafting finished with no attempts.", ephemeral=True)


__all__ = ["CraftingCog"]

