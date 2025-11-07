# nano-kontrol-2-fl-studio

A comprehensive FL Studio MIDI script that transforms your Korg nanoKONTROL2 into a powerful DAW controller with track group management, transport controls, and advanced playlist selection features.

## Features

### 🎚️ Track Group Management

- **8 Track Groups**: Control up to 8 groups of mixer tracks using the nanoKONTROL2's 8 channels
- **Group-Based Mixing**: Each fader controls all master tracks in a group simultaneously
- **Solo/Mute/Arm**: S/M/R buttons control entire track groups at once
- **Auto-Detection**: Automatically scans mixer track names on project load

### 🎮 Transport Controls

- **Play/Stop/Record**: Standard transport with LED feedback
- **Rewind/Fast Forward**: Quick navigation through your project
- **Loop Mode Toggle**: `MODE` toggles between song/pattern mode and sequencer visibility

### 🎵 Pattern/Instruments Navigation

- **Quick Instruments Switch**: `◄ PREV` or `► NEXT` to jump between instruments
- **Quick Pattern Switch**: `MODE` + (`◄ PREV` or `► NEXT`) to jump between patterns

### ✂️ Advanced Loop Tools

- **Bar-Snapped Navigation**: `MARKER ◄` or `MARKER ►` to move by 4 bars
- **Create Selections**: `MARKER SET` to create time selections
- **Move Selections**: `MARKER SET` + (`◄ PREV` or `► NEXT`) to move selection by its own length
- **Toggle Selections**: `MARKER ◄` + `MARKER ►` to save/restore selections
- **Fine Control**: Hold `►► FORWARD` during selection for 1-bar precision

### 🔄 Mixer Track Scanning

- **Press `◄ PREV` + `► NEXT` together**: Rescan mixer tracks

## Installation

Clone or download this repository to your FL Studio Hardware folder:

**Windows:**

```
C:\Users\[YourUsername]\Documents\Image-Line\FL Studio\Settings\Hardware\
```

**macOS:**

```
/Users/[YourUsername]/Documents/Image-Line/FL Studio/Settings/Hardware/
```

## Setup

### 1. MIDI Configuration

Configure your nanoKONTROL2 in FL Studio:

- Go to **Options > MIDI Settings**
- Assign an **input port** to **nanoKONTROL2**
- Assign an **output port** to **nanoKONTROL2**

### 2. Mixer Track Naming Convention

Your FL Studio mixer tracks must follow this naming pattern:

```
Track Groups:      Group Master Buses:
---------------    ----------------
Kick (1)           Drums [1]
Snare (1)
HiHat (1)

Bass (2)           Bass [2]
Sub Bass (2)

Lead (3)           Synths [3]
Pad (3)
Pluck (3)

Vocal (4)          Vocals [4]
Backing (4)

Guitar (5)         Guitar [5]
Guitar Reverb (5)

Piano (6)          Keys [6]
Rhodes (6)

FX (7)             FX [7]
Riser (7)

Ambient (8)        Atmosphere [8]
```

**Naming Rules:**

- **Group Members**: Use parentheses `(1)` through `(8)` in track name
- **Group Master Buses**: Use brackets `[1]` through `[8]` in track name
- A track can belong to only one group
- You can have **multiple master tracks** per group (e.g., `Drums [1]`, `Drums Reverb [1]`)
- All group masters are controlled together by the corresponding fader
- All tracks in a group respond to S/M/R buttons

### Example Mixer Setup

<img width="792" height="950" alt="image" src="https://github.com/user-attachments/assets/79f0bb48-b132-462c-8509-343fa925cc97" />

_Screenshot showing proper track naming convention in FL Studio mixer_

### 3. Config.py (Optional)

The default MIDI channel settings should work with standard nanoKONTROL2 configurations. Only edit `config.py` if your channels don't match the Korg Kontrol Editor settings:

- `MIDIChannel = 1` - MIDI channel for track buttons (S/M/R and faders)
- `TransportChan = 14` - MIDI channel for transport buttons

## nanoKONTROL2 Button Map

```
┌──────────────────────────────────────────────────────────┐
│  KORG nanoKONTROL2                                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [◄]  [►]  [SET] [◄M] [►M]  [◄◄] [►►] [■]  [▶] [●]      │
│  PREV NEXT  MODE PREV NEXT  REW  FWD  STOP PLAY REC      │
│                                                          │
│  [S] [S] [S] [S] [S] [S] [S] [S]  ← Solo                 │
│  [M] [M] [M] [M] [M] [M] [M] [M]  ← Mute                 │
│  [R] [R] [R] [R] [R] [R] [R] [R]  ← Arm/Record           │
│                                                          │
│  ═══ ═══ ═══ ═══ ═══ ═══ ═══ ═══                         │
│  ║║║ ║║║ ║║║ ║║║ ║║║ ║║║ ║║║ ║║║  ← Volume Faders        │
│  ║║║ ║║║ ║║║ ║║║ ║║║ ║║║ ║║║ ║║║    (Group Masters)      │
│   1   2   3   4   5   6   7   8                          │
└──────────────────────────────────────────────────────────┘
```

### Control Reference

**Mixer Scan:**

- `◄ PREV` + `► NEXT`: Rescan mixer tracks

**Transport Section:**

- `▶ PLAY`: Start playback
- `■ STOP`: Stop playback
- `● RECORD`: Start recording
- `◄◄ REWIND`: Rewind (hold for continuous)
- `►► FORWARD`: Fast forward (hold for continuous)
- `MODE`: Toggle between song/pattern mode

**Instruments / Patterns Navigation:**

- `◄ PREV`: Previous instrument
- `► NEXT`: Next instrument
- `MODE` + `◄ PREV`: Next pattern
- `MODE` + `► NEXT`: Previous pattern

**Marker/Selection:**

<img width="897" height="225" alt="image" src="https://github.com/user-attachments/assets/50a9834b-a3c5-43e1-8400-37f4bd62ea8f" />

- `MARKER ◄`: Move back 4 bars
- `MARKER ►`: Move forward 4 bars
- `►► FORWARD` + `MARKER ◄`: Move back 1 bar (fine control)
- `►► FORWARD` + `MARKER ►`: Move forward 1 bar (fine control)
- `MARKER SET`: Hold to create time selection
- `MARKER SET` + `◄ PREV`: Move selection backward by its own length
- `MARKER SET` + `► NEXT`: Move selection forward by its own length
- `MARKER ◄` + `MARKER ►`: Toggle save/restore selection

**Track Groups (Channels 1-8):**

- `S`: Solo track group (isolates group)
- `M`: Mute track group
- `R`: Arm group master for recording
- `Faders`: Control group master volume (max 80%)
- `Knobs`: Assign them to whatever you need

## Technical Details

- **Max Volume**: Faders are limited to 80% (FL Studio default volume)
- **FL Version**: Compatible with FL Studio 20+

## Troubleshooting

**Buttons don't light up:**

- Check MIDI output port is enabled in FL Studio settings

**Track groups don't respond:**

- Verify track naming follows the (1-8) and [1-8] convention exactly
- Press `◄ PREV` + `► NEXT` to rescan mixer tracks (buttons will flash twice)
- Check that at least one track has the proper naming for each group

**Volume faders don't work:**

- Verify group master tracks have [1-8] brackets in their names
- Ensure at least one master track exists for each group you want to control
- Check that group members route to their corresponding master tracks

## Credits

Script by Julien MEZIERE

Based on concepts from the nanoKONTROL2 community
