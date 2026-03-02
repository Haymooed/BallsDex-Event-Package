# BallsDex V3 Event Info Package 🎉
[![Support me on Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/MarketDexOfficial?utm_campaign=creatorshare_creator)
---

## 📦 Installation

Add the following entry to `config/extra.toml` so BallsDex installs the package automatically:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/Haymooed/BallsDex-Event-Package.git"
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

---

## 💬 Commands

### Player Commands

#### `/event info <event>`
View detailed information about a specific event.


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

## 🐛 Troubleshooting

### Event Not Found
- Ensure the event name matches exactly (case-insensitive)
- Check that the event is enabled in the admin panel
- Verify the event exists in the database

<img width="832" height="897" alt="image" src="https://github.com/user-attachments/assets/880aed1e-62c0-4988-88ff-d61eaf1f1749" />
