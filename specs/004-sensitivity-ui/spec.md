# Feature Specification: Sensitivity Dropdown for K-Means Bins

**Feature Branch**: `004-sensitivity-ui`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "the current sensitivity slider will be replaced by a dropdown that shows powers of 2 starting from 4 to 256 to configure the k-means bins"

## Clarifications

### Session 2025-01-27

- Q: Should the dropdown selection persist across image loads, or reset to "None" when a new image is loaded? → A: Reset to "None" when a new image is loaded
- Q: What happens when the dropdown value is changed while an image is being processed? → A: The dropdown should be disabled while the image is processed, so that no change of value is possible

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure K-Means Bins via Dropdown (Priority: P1)

Users can select the number of color bins for k-means clustering using a dropdown menu that displays powers of 2 (4, 8, 16, 32, 64, 128, 256) or "None" to disable color reduction, instead of using a continuous sensitivity slider. This provides direct control over the exact number of colors in the reduced palette or the ability to disable color reduction entirely.

**Why this priority**: This is the core functionality - replacing the slider with a dropdown that directly configures k-means bins. Without this, the feature cannot deliver value.

**Independent Test**: Can be fully tested by opening an image, selecting a value from the dropdown, and verifying that color reduction uses the selected number of bins. The test delivers immediate visual feedback showing the exact number of colors in the reduced image.

**Acceptance Scenarios**:

1. **Given** an image is loaded in the application, **When** the user selects "16" from the sensitivity dropdown, **Then** the image is reduced to exactly 16 colors using k-means clustering
2. **Given** an image is loaded, **When** the user changes the dropdown from "32" to "64", **Then** the image is re-processed with 64 color bins and displays more distinct colors
3. **Given** the dropdown is visible, **When** the user views the dropdown options, **Then** it displays exactly 8 options: None, 4, 8, 16, 32, 64, 128, 256
4. **Given** a color reduction has been applied, **When** the user selects a different value from the dropdown, **Then** the color reduction is immediately re-applied with the new bin count
5. **Given** an image is being processed, **When** the user attempts to change the dropdown value, **Then** the dropdown is disabled and no value change is possible until processing completes

---

### User Story 2 - Default Selection and Reset Behavior (Priority: P2)

The dropdown maintains a sensible default value and resets to "None" when a new image is loaded, ensuring each image starts with color reduction disabled.

**Why this priority**: Ensures predictable behavior - each new image starts with a clean slate (no color reduction). However, the feature is functional without this - it's a quality-of-life improvement.

**Independent Test**: Can be tested by selecting a dropdown value, loading a new image, and verifying the dropdown resets to "None". Also test that the default value is "None" when no image is loaded.

**Acceptance Scenarios**:

1. **Given** the application is opened with no image loaded, **When** the user views the sensitivity dropdown, **Then** it displays "None" as the default value (color reduction disabled)
2. **Given** the user has selected "128" from the dropdown for the current image, **When** they load a new image, **Then** the dropdown resets to "None" (color reduction disabled for the new image)
3. **Given** color reduction is disabled (value of "None"), **When** the user selects a value from the dropdown, **Then** color reduction is automatically enabled

---

### Edge Cases

- What happens when the dropdown value is changed while an image is being processed? (Resolved: The dropdown is disabled during image processing to prevent value changes)
- How does the system handle the transition from the old sensitivity slider (0.0-1.0) to the new dropdown (4-256 bins) for existing saved settings?
- What is the behavior if a user selects a bin count that results in processing errors (e.g., very small images with large bin counts)? (Resolved: ignore this case)
- How should the dropdown handle the case where no color reduction is desired? (Resolved: "None" option will be included and set as default)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST replace the sensitivity slider and spinbox with a dropdown menu in the controls panel
- **FR-002**: System MUST display exactly 8 options in the dropdown: None, 4, 8, 16, 32, 64, 128, 256 (where "None" disables color reduction, and the rest are powers of 2 from 4 to 256)
- **FR-003**: System MUST use the selected dropdown value directly as the k parameter for k-means clustering when a bin count is selected, or skip color reduction when "None" is selected (no conversion from sensitivity float)
- **FR-004**: System MUST apply color reduction immediately when the dropdown value changes
- **FR-005**: System MUST reset the dropdown to "None" when a new image is loaded
- **FR-006**: System MUST default to "None" when no image is loaded, disabling color reduction by default
- **FR-007**: System MUST reset all existing sensitivity float values (0.0-1.0) to the default "None" during migration to the new dropdown system
- **FR-008**: System MUST update the color reduction settings model to store the bin count instead of sensitivity float
- **FR-009**: System MUST emit a signal when the dropdown value changes, passing the selected bin count as an integer (or None/0 to represent disabled color reduction)
- **FR-010**: System MUST disable the dropdown while an image is being processed to prevent value changes during processing

### Key Entities

- **K-Means Bin Count**: The number of color clusters to generate during color reduction. Must be one of: None (disables color reduction), 4, 8, 16, 32, 64, 128, 256. Replaces the previous sensitivity float value (0.0-1.0) in the color reduction settings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select any of the 8 dropdown options (None, 4, 8, 16, 32, 64, 128, 256) and see immediate results (color reduction disabled for "None", or applied with the selected bin count)
- **SC-002**: Color reduction completes successfully for all 7 bin count values (4, 8, 16, 32, 64, 128, 256) without errors, regardless of image size or format. The "None" option successfully disables color reduction.
- **SC-003**: The dropdown resets to "None" when a new image is loaded, ensuring each image starts with color reduction disabled
- **SC-004**: Users can complete the transition from slider-based to dropdown-based color reduction configuration in under 5 seconds (selecting a value and seeing results)
- **SC-005**: The exact number of colors in the reduced image matches the selected bin count (within k-means clustering variance) for at least 95% of test cases

## Assumptions

- The dropdown will replace both the sensitivity slider and spinbox components entirely
- The k-means implementation already supports direct k parameter specification (it does via the optional `k` parameter in `reduce_colors`)
- Users prefer discrete, predictable bin counts over continuous sensitivity values for color reduction
- The powers of 2 (4, 8, 16, 32, 64, 128, 256) provide sufficient granularity for color reduction use cases
- The "None" option provides a clear way to disable color reduction without requiring a separate toggle
- Existing tests and integration points that use sensitivity float values will need to be updated to use bin counts

## Dependencies

- Requires the color reducer service to support direct k parameter specification (already implemented)
- Requires the settings model to be updated to store bin count instead of sensitivity float
- Requires the main controller to accept bin count integers instead of sensitivity floats
- May require updates to operation history if it stores sensitivity values

## Out of Scope

- Adding more bin count options beyond the 7 specified powers of 2 (plus the "None" option)
- Supporting custom bin counts entered by users
- Maintaining backward compatibility with the old sensitivity slider interface
- Providing a visual preview of how different bin counts will affect the image before selection
