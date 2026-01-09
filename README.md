# BallsDex V3 Event Info Package 🎉

The **Event Info Package** for **BallsDex V3** adds a clean way to display **event-based ball information** using slash commands. It is **not a new card type**, but an information layer that shows event details, associated balls, and importance.

This package is fully configurable through the **admin panel** and follows the **same structure and conventions** as the Merchant and Crafting packages.

---

## 📦 Installation

Add the following entry to `config/extra.toml` so BallsDex installs the package automatically:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/Haymooed/MarketDex-PackagesV3.git"
path = "event"
enabled = true
editable = false
```

The package is distributed as a standard Python package — no manual file copying required.

After adding the configuration, restart your BallsDex bot. The package will be automatically installed and migrations will be run.

---

## 🎯 Features

- **Event Management**: Create and manage events through the Django admin panel
- **Event Types**: Support for both permanent and limited-time events
- **Ball Association**: Link multiple balls to events and highlight important ones
- **Status Display**: Automatic status calculation (Active, Upcoming, Ended, Permanent)
- **Clean Embeds**: Beautiful, informative Discord embeds with color-coded status
- **Slash Commands**: Easy-to-use commands for players to view event information

---

## 🛠️ Admin Panel Integration

All event data must be managed through the admin panel. Navigate to the Django admin interface and find the **"Event Info"** section.

### Creating an Event

1. Go to **Event Info → Events → Add Event**
2. Fill in the basic information:
   - **Name**: Unique name for the event (e.g., "Summer Collection 2024")
   - **Description**: Detailed description of the event
   - **Enabled**: Toggle to show/hide the event from players

### Event Type Configuration

Choose one of two event types:

#### Permanent Events
- Set **Is Permanent** to `True`
- Start and end dates are ignored
- Status will always show as "🟢 Permanent Event"

#### Limited-Time Events
- Set **Is Permanent** to `False`
- Set **Start Date** (optional): When the event becomes active
- Set **End Date** (optional): When the event ends
- Status will be calculated automatically:
  - **🟡 Upcoming**: Current time < Start Date
  - **🟢 Active**: Current time between Start Date and End Date
  - **🔴 Ended**: Current time > End Date

### Adding Balls to Events

1. **Included Balls**: Select all balls that are part of this event
   - Use the filter horizontal widget to easily search and select balls
   - These will be displayed in the "Included Balls" section

2. **Important Balls**: Select featured/highlighted balls (subset of included balls)
   - These will be displayed with a ⭐ icon in the "Featured Balls" section
   - Should be a subset of the included balls for best UX

### Event Statistics

The admin panel displays helpful statistics:
- **Status**: Current status of the event (with color indicators)
- **Included Balls**: Count of balls included in the event
- **Important Balls**: Count of featured balls

---

## 💬 Commands

### Player Commands

#### `/event info <event>`
View detailed information about a specific event.

**Parameters:**
- `event` (required): The name of the event to view (case-insensitive)

**Example:**
```
/event info event:Summer Collection 2024
```

#### `/balls event <event>`
Alternative alias showing the same information as `/event info`.

**Parameters:**
- `event` (required): The name of the event to view (case-insensitive)

**Example:**
```
/balls event event:Summer Collection 2024
```

> **Note**: The `/balls event` command may conflict if your main BallsDex bot already has a `/balls` command group. In that case, only `/event info` will be available, or you may need to manually integrate the command into your existing `/balls` group.

---

## 📊 Embed Output

The event embed displays the following information:

### Header
- **Event Name**: The name of the event
- **Description**: Full description of the event
- **Color**: Status-based color coding
  - 🟢 Green: Active or Permanent events
  - 🟡 Gold: Upcoming events
  - 🔴 Red: Ended events

### Fields

1. **Status**
   - 🟢 Permanent Event
   - 🟢 Active
   - 🟡 Upcoming
   - 🔴 Ended

2. **Availability**
   - For permanent events: "**Permanent Event**"
   - For limited-time events: Start and end dates formatted as "Jan 1, 2024 at 12:00 PM"

3. **Included Balls**
   - Lists all balls included in the event
   - Shows up to 20 balls, with a count indicator if more exist
   - Format: "Ball1, Ball2, Ball3... (+5 more)"

4. **⭐ Featured Balls**
   - Lists important/featured balls with a ⭐ prefix
   - Shows up to 10 balls, with a count indicator if more exist
   - Only displayed if important balls are configured

### Footer
- **Event ID**: Internal ID for reference

---

## 🔧 Behavior Requirements

- **Visibility**: Events only display if `enabled=True` in the admin panel
- **Status Calculation**: Status is calculated based on current time and event dates
- **Case Insensitive**: Event name matching is case-insensitive
- **Informational Only**: Commands are read-only and do not spawn balls or provide rewards
- **Error Handling**: Gracefully handles missing or disabled events with helpful error messages

---

## 📝 Example Event Configuration

### Example 1: Permanent Event

```
Name: "Halloween Collection"
Description: "Spooky balls available year-round!"
Is Permanent: True
Enabled: True
Included Balls: [Pumpkin, Ghost, Witch, Skeleton]
Important Balls: [Pumpkin, Ghost]
```

**Result**: Always shows as "🟢 Permanent Event" with no dates.

### Example 2: Limited-Time Event

```
Name: "Summer Sale 2024"
Description: "Limited-time summer-themed balls!"
Is Permanent: False
Start Date: June 1, 2024 00:00:00
End Date: August 31, 2024 23:59:59
Enabled: True
Included Balls: [Sun, Beach, Ice Cream, Palm Tree]
Important Balls: [Sun, Beach]
```

**Result**: 
- Before June 1: Shows as "🟡 Upcoming"
- June 1 - August 31: Shows as "🟢 Active"
- After August 31: Shows as "🔴 Ended"

---

## 🏗️ Technical Details

### Models

- **Event**: Main model storing event information
  - Fields: name, description, enabled, is_permanent, start_date, end_date
  - Relationships: ManyToMany with Ball (included_balls, important_balls)
  - Methods: `get_status()`, `is_currently_active()`

### Admin Integration

- Full Django admin integration with:
  - List view with filters and search
  - Form view with organized fieldsets
  - Filter horizontal for ball selection
  - Read-only statistics display

### Commands

- Uses `discord.ext.commands.GroupCog` for command organization
- Implements `app_commands` for slash command support
- Follows BallsDex V3 async patterns with `sync_to_async`

### Compatibility

- Fully compatible with BallsDex V3 models (Ball, Special)
- Uses Django ORM async methods (`aget`, `aall`, etc.)
- Follows the BallsDex V3 custom package guide

---

## 🐛 Troubleshooting

### Event Not Found
- Ensure the event name matches exactly (case-insensitive)
- Check that the event is enabled in the admin panel
- Verify the event exists in the database

### `/balls event` Command Not Available
- The main BallsDex bot may already have a `/balls` command group
- Use `/event info` instead, which will always be available
- If you need `/balls event`, manually integrate it into your existing `/balls` group

### Status Not Updating
- Status is calculated in real-time based on server timezone
- Ensure your Django `TIME_ZONE` setting is correct
- Check that start/end dates are set correctly for limited-time events

---

## 📚 Related Documentation

- [BallsDex V3 Custom Package Guide](https://wiki.ballsdex.com/dev/custom-package/)
- [BallsDex Merchant Package](https://github.com/Haymooed/BallsDex-Merchant-Package) (similar structure reference)

---

## 📄 License

This package follows the same license as the main BallsDex project.

---

## 🤝 Contributing

This package follows the same structure and conventions as other BallsDex V3 packages. When contributing:

1. Follow the existing code style
2. Ensure all admin panel functionality works correctly
3. Test commands in a development environment
4. Update this README if adding new features

---

## ✨ Credits

Created following the BallsDex V3 package structure and conventions.
