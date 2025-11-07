# Project Architecture

This FL Studio MIDI script for nanoKONTROL2 is organized into modular components for better maintainability and testing.

## File Structure

```
nano-kontrol-2-fl-studio/
├── device_nanoKONTROL2.py    # Main entry point
├── config.py                  # User configuration
├── README.md
├── LICENSE
├── ARCHITECTURE.md
├── core/                      # Core infrastructure
│   ├── __init__.py
│   ├── constants.py          # Hardware mappings & constants
│   ├── fl_studio_api.py      # FL Studio API wrapper
│   └── hardware_interface.py # MIDI communication
└── controllers/               # Controller components
    ├── __init__.py
    ├── ui/                    # User interface (LEDs)
    │   ├── __init__.py
    │   └── button_light_controller.py
    ├── controls/              # Specific control handlers
    │   ├── __init__.py
    │   ├── transport_controller.py
    │   ├── navigation_controller.py
    │   ├── pattern_controller.py
    │   └── loop_mode_controller.py
    └── managers/              # High-level orchestration
        ├── __init__.py
        ├── general_controls_manager.py
        ├── selection_manager.py
        └── tracks_manager.py
```

## Component Overview

### Main Entry Point

**`device_nanoKONTROL2.py`** - Main FL Studio callback handlers and dependency injection root

**FL Studio Callbacks:**

- `OnInit()` - Create FLStudioAPI wrapper, initialize HardwareInterface, TracksManager, and GeneralControlsManager with dependency injection
- `OnProjectLoad()` - Trigger mixer track scan
- `OnRefresh()` - Update button LED states when FL Studio state changes
- `OnControlChange()` - Route MIDI events from hardware to appropriate controllers

**Why this is the main entry point:**

- Only file with access to FL Studio API functions in global scope
- Creates the `FLStudioAPI` wrapper containing all FL Studio function references
- Injects dependencies into all controllers
- Acts as the "composition root" for dependency injection

### Core Infrastructure (`core/`)

#### **`constants.py`**

Hardware button mappings and application constants.

- Button IDs (PLAY_BUTTON, STOP_BUTTON, etc.)
- Channel configurations
- Timing constants (bar lengths, etc.)

#### **`fl_studio_api.py`**

Wrapper class for FL Studio API functions enabling dependency injection.

- `FLStudioAPI` class - Stores references to FL Studio API functions
- Enables controllers to access FL Studio functions outside main script scope
- Supports testability by allowing API mocking

#### **`hardware_interface.py`**

Low-level MIDI communication class.

- `HardwareInterface` class - Wraps MIDI output operations
- `updateButtonLight()` - Control individual LED states
- `updateTracksButtons()` - Bulk LED updates

### Controllers (`controllers/`)

#### UI Layer (`ui/`)

**`button_light_controller.py`** - Manages all LED/button light states on the hardware.

- Update individual button lights
- Sync transport button states with FL Studio

#### Control Handlers (`controls/`)

**`transport_controller.py`** - Controls playback transport.

- Play/Stop/Record
- Rewind/Fast forward with LED feedback

**`navigation_controller.py`** - Handles track/channel navigation.

- Next/Previous track
- Trigger mixer scan (when both buttons pressed simultaneously)

**`pattern_controller.py`** - Manages pattern switching and mode button behavior.

- Switch patterns when mode button is held
- Track whether to toggle loop mode on release
- Prevent accidental loop mode changes during pattern navigation

**`loop_mode_controller.py`** - Controls loop mode and sequencer window visibility.

- Toggle between song/pattern mode
- Auto-show/hide sequencer window

#### Managers (`managers/`)

**`general_controls_manager.py`** - Coordinator class that orchestrates all controllers based on button context.

- Routes button presses to appropriate controllers
- Handles contextual behavior (e.g., mode button combinations)
- Manages state-dependent button actions

**`selection_manager.py`** - Handles timeline selection and marker navigation.

- Create/modify/move selections
- Navigate by bars (with adjustable accuracy)
- Save/restore previous selections
- Timeline navigation with snap-to-bar

**`tracks_manager.py`** - Manages mixer track groups.

- Solo/Mute/Arm track groups by naming convention
- Volume faders for master tracks
- Scan mixer for tracks with group notation: `(N)` for group members, `[N]` for masters
- Intelligent solo behavior (auto-unmute group members)

## Data Flow

```
Hardware Button Press
        ↓
device_nanoKONTROL2.py (OnControlChange)
        ↓
GeneralControlsManager (routing logic)
        ↓
Specific Controller (SelectionManager, TransportController, etc.)
        ↓
FLStudioAPI (wrapper) → FL Studio Functions
        ↓
ButtonLightController (update LED feedback)
        ↓
HardwareInterface (MIDI out) → FLStudioAPI
        ↓
Hardware LEDs Updated
```

### Initialization Flow

```
OnInit()
        ↓
Create FLStudioAPI (inject all FL Studio functions)
        ↓
Create HardwareInterface (inject FLStudioAPI)
        ↓
Create TracksManager (inject HardwareInterface + FLStudioAPI)
        ↓
Create GeneralControlsManager (inject HardwareInterface + FLStudioAPI)
        ↓
  GeneralControlsManager creates sub-controllers:
  - ButtonLightController (HardwareInterface + FLStudioAPI)
  - SelectionManager (ButtonLightController + FLStudioAPI)
  - TransportController (ButtonLightController + FLStudioAPI)
  - NavigationController (ButtonLightController + FLStudioAPI)
  - PatternController (FLStudioAPI)
  - LoopModeController (FLStudioAPI)
```

## Key Design Patterns

### Single Responsibility Principle

Each controller class has one clear responsibility and focused purpose. UI concerns are separated from business logic, which is separated from low-level hardware communication.

### Dependency Injection

All controllers receive their dependencies via constructor parameters, enabling:

- **Testability** - Dependencies can be mocked for unit testing
- **Flexibility** - Easy to swap implementations
- **Decoupling** - Controllers don't create their own dependencies

Example: `ButtonLightController(hardwareInterface, flApi)`

### FL Studio API Wrapper Pattern

**Problem**: FL Studio API functions are only available in the main script scope. Sub-modules cannot directly import them.

**Solution**: `FLStudioAPI` class wraps all FL Studio functions and is passed to controllers.

```python
# In device_nanoKONTROL2.py (main script)
flApi = FLStudioAPI({
    'midiOutMsg': midiOutMsg,
    'start': start,
    'stop': stop,
    # ... all other FL Studio functions
})

# Controllers access via flApi instance
self.flApi.start()
self.flApi.midiOutMsg(...)
```

This pattern:

- Solves Python scope limitations in FL Studio's environment
- Enables dependency injection throughout the codebase
- Makes the codebase testable (can mock the API)

### Static Helper Methods

Common calculations extracted into reusable static methods in `TracksManager`:

- `getGroupIndexFromButton()` - Calculate group index from button ID
- `getSoloButton()`, `getMuteButton()`, `getArmButton()` - Calculate button IDs
- `validateGroupIndex()` - Validate and return group index or None

These methods don't need instance state and can be called without creating an object.

### Context-Aware Routing

The `GeneralControlsManager` changes button behavior based on current state:

- **Selection active** → Prev/Next moves selection instead of changing tracks
- **Mode button pressed** → Prev/Next changes patterns instead of tracks
- **Forward button in selection mode** → Increases selection accuracy to single bar

This allows the same physical buttons to have different functions based on context.

### State Management

Controllers maintain state for complex interactions:

- **Button press/release tracking** - Detect button combinations (e.g., both track buttons = trigger scan)
- **Selection history** - Save/restore previous selections
- **Pattern movement tracking** - Prevent unintended loop mode toggles when switching patterns

### Naming Conventions

- **camelCase** for variables and parameters: `hardwareInterface`, `flApi`, `lightController`
- **camelCase** for methods: `updateButtonLight()`, `getGroupIndex()`, `armTrack()`
- **PascalCase** for classes: `FLStudioAPI`, `HardwareInterface`, `TracksManager`
- **UPPER_SNAKE_CASE** for constants: `PLAY_BUTTON`, `MAX_VOLUME`, `ONE_BAR_IN_TICKS`
- **No underscore prefixes** - All methods are public (Python convention)

## Directory Organization Rationale

### `controllers/ui/`

Contains components responsible for visual feedback (LED states). Separated because UI concerns are distinct from business logic.

### `controllers/controls/`

Contains specific, focused control handlers for individual hardware features. Each controller handles one type of control (transport, navigation, etc.).

### `controllers/managers/`

Contains higher-level orchestration and state management. These components coordinate multiple controls and manage complex state.

## Benefits

✅ **Modular** - Each component can be tested/modified independently  
✅ **Readable** - Clear file names and directory structure indicate purpose  
✅ **Maintainable** - Changes isolated to specific files  
✅ **Extensible** - Easy to add new controllers or features  
✅ **DRY** - No code duplication across modules  
✅ **Organized** - Three-layer hierarchy (core/controllers/business logic)  
✅ **Scalable** - Can add more controls without cluttering directories  
✅ **Testable** - Dependency injection enables unit testing with mocked dependencies  
✅ **Consistent** - Unified camelCase naming convention throughout  
✅ **FL Studio Compatible** - API wrapper solves Python scope limitations in FL Studio environment
