# BallsDex V3 Crafting Package 🛠️

The **Crafting Package** for **BallsDex V3** allows players to combine items and materials to create new collectibles. The system is fully configurable via the **admin panel** and follows the **same structure and conventions** as the BallsDex V3 Merchant Package.

This package is designed to integrate cleanly with the BallsDex V3 custom package system.

---

## Installation (`extra.toml`)

Add the following entry to `config/extra.toml` so BallsDex installs the package automatically:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/Haymooed/BallsDex-Crafting-Package.git"
path = "crafting"
enabled = true
editable = false
```

The package is distributed as a standard Python package — no manual file copying required.

---

## Admin Panel Integration

The crafting system works entirely through the admin panel, following the same format and patterns used by the BallsDex V3 Merchant Package.

No values are hardcoded. All settings and data are editable from the panel.

### Configuration

Configuration follows the BallsDex V3 custom package guidelines:
https://wiki.ballsdex.com/dev/custom-package/

#### Crafting Settings (singleton)
- Enable / disable crafting
- Craft cooldown (seconds)
- Auto-crafting toggle
- Success rate handling (if enabled)
- Default success rate

#### Crafting Recipes
- Required ingredients (items / balls / specials)
- Quantity per ingredient
- Result item or BallInstance
- Optional specials or bonuses
- Optional craft cost
- Per-recipe success rate

All crafting actions are logged for moderation, balance, and auditing.

---

## Commands (Slash Commands / app_commands)

### Player Commands

- `/craft view` — View all available crafting recipes.
- `/craft craft <recipe_id>` — Craft a recipe; consumes ingredients, enforces cooldowns, and grants rewards.
- `/craft auto <recipe_id|0>` — Automatically craft a selected recipe whenever requirements are met (until disabled).

### Admin Commands

- `/craft bulk_add <json_definition>` — Bulk add crafting recipes from a JSON definition (administrator only).

---

## Behaviour Requirements

- Recipes are only available when crafting is enabled.
- Crafting validates all requirements before execution.
- Auto-crafting respects cooldowns and resource availability.
- Crafting fails gracefully with clear user feedback.
- All crafting attempts are logged for auditing.

---

## Technical Notes

- Follows the same file structure, setup flow, and patterns as the Merchant Package.
- Uses async `setup(bot)` and modern `app_commands`.
- Fully compatible with BallsDex V3 models (Ball, BallInstance, Player, Special).
- Designed to plug directly into the BallsDex V3 extra/custom package loader.
- Uses `django-solo` for singleton settings management.

This package feels native to BallsDex V3, consistent with existing official and community packages, and easy for admins to manage through the panel.

---

## License

MIT License
