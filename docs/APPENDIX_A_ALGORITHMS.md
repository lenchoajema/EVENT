# Appendix A: Algorithm Specifications
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Roadmap to Scale](./ROADMAP_TO_SCALE.md)

---

## Appendix A: Algorithm Specifications

Detailed mathematical formulations and pseudocode for core EVENT algorithms.

---

### A.1 YOLOv8 Object Detection

#### Mathematical Formulation

YOLOv8 performs single-stage object detection by dividing the input image into a grid and predicting bounding boxes and class probabilities for each grid cell.

**Network Architecture:**

$$
f_{\theta}: \mathbb{R}^{H \times W \times 3} \rightarrow \mathbb{R}^{G \times G \times (B \times (5 + C))}
$$

Where:
- $H \times W$: Input image dimensions (640×640 default)
- $G \times G$: Output grid size (varies by scale: 80×80, 40×40, 20×20)
- $B$: Number of anchor boxes per grid cell (3)
- $C$: Number of classes (3 for EVENT: person, vehicle, animal)
- $5$: Box parameters (x, y, w, h, confidence)

**Bounding Box Prediction:**

$$
\begin{aligned}
b_x &= \sigma(t_x) + c_x \\
b_y &= \sigma(t_y) + c_y \\
b_w &= p_w \cdot e^{t_w} \\
b_h &= p_h \cdot e^{t_h}
\end{aligned}
$$

Where:
- $(t_x, t_y, t_w, t_h)$: Network outputs
- $(c_x, c_y)$: Grid cell coordinates
- $(p_w, p_h)$: Anchor box dimensions
- $\sigma$: Sigmoid activation
- $(b_x, b_y, b_w, b_h)$: Predicted box coordinates

**Objectness Score:**

$$
P(\text{object}) = \sigma(t_o)
$$

**Class Probability:**

$$
P(\text{class}_i | \text{object}) = \text{softmax}(t_{c_1}, \ldots, t_{c_C})_i
$$

**Loss Function:**

$$
\mathcal{L} = \lambda_{\text{box}} \mathcal{L}_{\text{box}} + \lambda_{\text{obj}} \mathcal{L}_{\text{obj}} + \lambda_{\text{cls}} \mathcal{L}_{\text{cls}}
$$

**Box Regression Loss (CIoU):**

$$
\mathcal{L}_{\text{box}} = 1 - \text{CIoU} + \frac{\rho^2(b, b^{gt})}{c^2} + \alpha v
$$

Where:
- $\text{CIoU}$: Complete Intersection over Union
- $\rho$: Euclidean distance between box centers
- $c$: Diagonal length of smallest enclosing box
- $v$: Aspect ratio consistency
- $\alpha$: Trade-off parameter

**Non-Maximum Suppression (NMS):**

$$
\text{keep}(b_i) = \begin{cases}
\text{True} & \text{if } \max_{j \neq i} \text{IoU}(b_i, b_j) < \tau_{\text{NMS}} \\
\text{False} & \text{otherwise}
\end{cases}
$$

Where $\tau_{\text{NMS}} = 0.45$ (NMS threshold)

#### Pseudocode

```python
def yolov8_inference(image, model, confidence_threshold=0.5):
    """
    YOLOv8 inference pipeline.
    
    Args:
        image: Input image (H, W, 3)
        model: YOLOv8 ONNX model
        confidence_threshold: Minimum confidence for detections
    
    Returns:
        List of detections [(x, y, w, h, confidence, class_id), ...]
    """
    # 1. Preprocess image
    img_resized = resize(image, (640, 640))
    img_normalized = img_resized / 255.0
    img_transposed = transpose(img_normalized, (2, 0, 1))  # CHW format
    img_batch = expand_dims(img_transposed, axis=0)  # Add batch dimension
    
    # 2. Forward pass
    outputs = model.run(img_batch)  # Shape: (1, 8400, 8)
    # 8400 = (80×80 + 40×40 + 20×20) × 3 anchors = 8400 predictions
    # 8 = (x, y, w, h, confidence, class1, class2, class3)
    
    predictions = outputs[0][0]  # Remove batch dimension
    
    # 3. Decode predictions
    detections = []
    for pred in predictions:
        x_center, y_center, width, height, objectness, *class_scores = pred
        
        # Check objectness threshold
        if objectness < confidence_threshold:
            continue
        
        # Get class with highest score
        class_id = argmax(class_scores)
        class_confidence = class_scores[class_id]
        
        # Combined confidence
        confidence = objectness * class_confidence
        
        if confidence < confidence_threshold:
            continue
        
        # Convert from center format to corner format
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        
        # Scale back to original image size
        scale_x = image.width / 640
        scale_y = image.height / 640
        
        x1 *= scale_x
        y1 *= scale_y
        width *= scale_x
        height *= scale_y
        
        detections.append((x1, y1, width, height, confidence, class_id))
    
    # 4. Non-Maximum Suppression
    detections = non_max_suppression(detections, iou_threshold=0.45)
    
    return detections

def non_max_suppression(detections, iou_threshold=0.45):
    """NMS to eliminate duplicate detections."""
    if not detections:
        return []
    
    # Sort by confidence (descending)
    detections = sorted(detections, key=lambda x: x[4], reverse=True)
    
    keep = []
    while detections:
        # Keep highest confidence detection
        best = detections.pop(0)
        keep.append(best)
        
        # Remove overlapping detections
        detections = [
            det for det in detections
            if iou(best, det) < iou_threshold
        ]
    
    return keep

def iou(box1, box2):
    """Calculate Intersection over Union."""
    x1_1, y1_1, w1, h1, _, _ = box1
    x1_2, y1_2, w2, h2, _, _ = box2
    
    x2_1, y2_1 = x1_1 + w1, y1_1 + h1
    x2_2, y2_2 = x1_2 + w2, y1_2 + h2
    
    # Intersection
    xi1 = max(x1_1, x1_2)
    yi1 = max(y1_1, y1_2)
    xi2 = min(x2_1, x2_2)
    yi2 = min(y2_1, y2_2)
    
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    
    # Union
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0
```

**Complexity Analysis:**
- Forward pass: $O(HW)$ per layer, $O(L \cdot HW)$ for $L$ layers
- NMS: $O(N^2)$ where $N$ is number of detections (typically $N < 100$)
- Overall: $O(L \cdot HW + N^2)$, dominated by forward pass

---

### A.2 Kalman Filter Tracking

#### Mathematical Formulation

The Kalman filter estimates the state of a moving object from noisy observations.

**State Vector:**

$$
\mathbf{x}_t = \begin{bmatrix} x \\ y \\ \dot{x} \\ \dot{y} \end{bmatrix} \in \mathbb{R}^4
$$

**State Transition Model:**

$$
\mathbf{x}_t = \mathbf{F} \mathbf{x}_{t-1} + \mathbf{w}_t
$$

Where:

$$
\mathbf{F} = \begin{bmatrix}
1 & 0 & \Delta t & 0 \\
0 & 1 & 0 & \Delta t \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}, \quad \mathbf{w}_t \sim \mathcal{N}(0, \mathbf{Q})
$$

**Process Noise Covariance:**

$$
\mathbf{Q} = \sigma_a^2 \begin{bmatrix}
\frac{\Delta t^4}{4} & 0 & \frac{\Delta t^3}{2} & 0 \\
0 & \frac{\Delta t^4}{4} & 0 & \frac{\Delta t^3}{2} \\
\frac{\Delta t^3}{2} & 0 & \Delta t^2 & 0 \\
0 & \frac{\Delta t^3}{2} & 0 & \Delta t^2
\end{bmatrix}
$$

Where $\sigma_a^2$ is the acceleration noise variance.

**Observation Model:**

$$
\mathbf{z}_t = \mathbf{H} \mathbf{x}_t + \mathbf{v}_t
$$

Where:

$$
\mathbf{H} = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0
\end{bmatrix}, \quad \mathbf{v}_t \sim \mathcal{N}(0, \mathbf{R})
$$

**Observation Noise Covariance:**

$$
\mathbf{R} = \begin{bmatrix}
\sigma_x^2 & 0 \\
0 & \sigma_y^2
\end{bmatrix}
$$

**Prediction Step:**

$$
\begin{aligned}
\hat{\mathbf{x}}_{t|t-1} &= \mathbf{F} \hat{\mathbf{x}}_{t-1|t-1} \\
\mathbf{P}_{t|t-1} &= \mathbf{F} \mathbf{P}_{t-1|t-1} \mathbf{F}^T + \mathbf{Q}
\end{aligned}
$$

**Update Step:**

$$
\begin{aligned}
\mathbf{y}_t &= \mathbf{z}_t - \mathbf{H} \hat{\mathbf{x}}_{t|t-1} \quad \text{(Innovation)} \\
\mathbf{S}_t &= \mathbf{H} \mathbf{P}_{t|t-1} \mathbf{H}^T + \mathbf{R} \quad \text{(Innovation covariance)} \\
\mathbf{K}_t &= \mathbf{P}_{t|t-1} \mathbf{H}^T \mathbf{S}_t^{-1} \quad \text{(Kalman gain)} \\
\hat{\mathbf{x}}_{t|t} &= \hat{\mathbf{x}}_{t|t-1} + \mathbf{K}_t \mathbf{y}_t \\
\mathbf{P}_{t|t} &= (\mathbf{I} - \mathbf{K}_t \mathbf{H}) \mathbf{P}_{t|t-1}
\end{aligned}
$$

#### Pseudocode

```python
def kalman_filter_track(observation, state, covariance, dt):
    """
    Kalman filter prediction and update.
    
    Args:
        observation: Current measurement (x, y)
        state: Previous state [x, y, vx, vy]
        covariance: Previous covariance matrix P (4×4)
        dt: Time step
    
    Returns:
        Updated state and covariance
    """
    # Constants
    sigma_a = 0.5  # Acceleration noise std dev (m/s²)
    sigma_x = 2.0  # Position measurement noise std dev (m)
    sigma_y = 2.0
    
    # State transition matrix F
    F = np.array([
        [1, 0, dt, 0],
        [0, 1, 0, dt],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    # Process noise covariance Q
    Q = (sigma_a ** 2) * np.array([
        [dt**4/4, 0, dt**3/2, 0],
        [0, dt**4/4, 0, dt**3/2],
        [dt**3/2, 0, dt**2, 0],
        [0, dt**3/2, 0, dt**2]
    ])
    
    # Observation matrix H
    H = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0]
    ])
    
    # Observation noise covariance R
    R = np.array([
        [sigma_x**2, 0],
        [0, sigma_y**2]
    ])
    
    # PREDICTION
    state_pred = F @ state
    covariance_pred = F @ covariance @ F.T + Q
    
    # UPDATE
    innovation = observation - (H @ state_pred)
    innovation_cov = H @ covariance_pred @ H.T + R
    kalman_gain = covariance_pred @ H.T @ np.linalg.inv(innovation_cov)
    
    state_updated = state_pred + kalman_gain @ innovation
    covariance_updated = (np.eye(4) - kalman_gain @ H) @ covariance_pred
    
    return state_updated, covariance_updated

def hungarian_assignment(cost_matrix):
    """
    Hungarian algorithm for optimal assignment.
    
    Args:
        cost_matrix: N×M matrix of assignment costs
    
    Returns:
        List of (row, col) assignments
    """
    from scipy.optimize import linear_sum_assignment
    
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return list(zip(row_ind, col_ind))

def multi_object_tracking(detections, tracks, max_distance=50):
    """
    Track multiple objects using Kalman filter + Hungarian assignment.
    
    Args:
        detections: List of new detections [(x, y, class, confidence), ...]
        tracks: List of existing tracks [Track, ...]
        max_distance: Maximum distance for association (meters)
    
    Returns:
        Updated tracks
    """
    if not tracks:
        # Initialize new tracks
        return [Track(det) for det in detections]
    
    # Build cost matrix (distances between predictions and detections)
    n_tracks = len(tracks)
    n_detections = len(detections)
    
    cost_matrix = np.zeros((n_tracks, n_detections))
    
    for i, track in enumerate(tracks):
        predicted_pos = track.predict()
        
        for j, detection in enumerate(detections):
            det_pos = detection[:2]
            distance = np.linalg.norm(predicted_pos - det_pos)
            
            # Use large cost if too far
            cost_matrix[i, j] = distance if distance < max_distance else 1e6
    
    # Solve assignment problem
    assignments = hungarian_assignment(cost_matrix)
    
    # Update assigned tracks
    assigned_tracks = set()
    assigned_detections = set()
    
    for track_idx, det_idx in assignments:
        if cost_matrix[track_idx, det_idx] < max_distance:
            tracks[track_idx].update(detections[det_idx])
            assigned_tracks.add(track_idx)
            assigned_detections.add(det_idx)
    
    # Create new tracks for unassigned detections
    for det_idx, detection in enumerate(detections):
        if det_idx not in assigned_detections:
            tracks.append(Track(detection))
    
    # Remove tracks that haven't been updated (lost tracks)
    tracks = [t for i, t in enumerate(tracks) 
              if i in assigned_tracks or t.age < 5]
    
    return tracks
```

**Complexity Analysis:**
- Prediction: $O(n^3)$ for $n×n$ matrix operations (small $n=4$, effectively $O(1)$)
- Update: $O(n^3)$ for matrix inversion
- Hungarian algorithm: $O(N^3)$ where $N = \max(\text{tracks}, \text{detections})$
- Overall: $O(N^3)$ per frame

---

### A.3 A* Path Planning

#### Mathematical Formulation

A* finds the shortest path in a weighted graph using heuristic search.

**Cost Function:**

$$
f(n) = g(n) + h(n)
$$

Where:
- $g(n)$: Actual cost from start to node $n$
- $h(n)$: Heuristic estimated cost from $n$ to goal
- $f(n)$: Total estimated cost through $n$

**Heuristic (Euclidean Distance):**

$$
h(n) = \sqrt{(x_n - x_{\text{goal}})^2 + (y_n - y_{\text{goal}})^2}
$$

**Admissibility Condition:**

$$
h(n) \leq h^*(n) \quad \forall n
$$

Where $h^*(n)$ is the true cost to goal. This ensures optimality.

#### Pseudocode

```python
def a_star(start, goal, grid, obstacle_map):
    """
    A* pathfinding algorithm.
    
    Args:
        start: (x, y) start position
        goal: (x, y) goal position
        grid: Grid resolution (meters)
        obstacle_map: 2D array of obstacles (1=obstacle, 0=free)
    
    Returns:
        Path as list of (x, y) waypoints, or None if no path exists
    """
    from heapq import heappush, heappop
    
    def heuristic(pos):
        """Euclidean distance heuristic."""
        return np.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
    
    def get_neighbors(pos):
        """Get valid neighboring cells (8-connected)."""
        x, y = pos
        neighbors = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if 0 <= nx < obstacle_map.shape[0] and 0 <= ny < obstacle_map.shape[1]:
                    # Check if free
                    if obstacle_map[nx, ny] == 0:
                        # Cost is sqrt(2) for diagonal, 1 for straight
                        cost = 1.414 if (dx != 0 and dy != 0) else 1.0
                        neighbors.append(((nx, ny), cost))
        
        return neighbors
    
    # Initialize
    open_set = []  # Priority queue: (f_score, counter, node)
    closed_set = set()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start)}
    
    counter = 0  # Tie-breaker for heap
    heappush(open_set, (f_score[start], counter, start))
    
    while open_set:
        _, _, current = heappop(open_set)
        
        # Goal reached
        if current == goal:
            return reconstruct_path(came_from, current)
        
        closed_set.add(current)
        
        # Explore neighbors
        for neighbor, edge_cost in get_neighbors(current):
            if neighbor in closed_set:
                continue
            
            tentative_g = g_score[current] + edge_cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                # Better path found
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                
                counter += 1
                heappush(open_set, (f_score[neighbor], counter, neighbor))
    
    # No path found
    return None

def reconstruct_path(came_from, current):
    """Reconstruct path from goal to start."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]  # Reverse to get start→goal

def smooth_path(path, obstacle_map):
    """
    Smooth path by removing unnecessary waypoints.
    
    Uses line-of-sight to eliminate intermediate waypoints.
    """
    if len(path) <= 2:
        return path
    
    smoothed = [path[0]]
    current_idx = 0
    
    while current_idx < len(path) - 1:
        # Find farthest visible point
        farthest = current_idx + 1
        
        for i in range(current_idx + 2, len(path)):
            if has_line_of_sight(path[current_idx], path[i], obstacle_map):
                farthest = i
            else:
                break
        
        smoothed.append(path[farthest])
        current_idx = farthest
    
    return smoothed

def has_line_of_sight(p1, p2, obstacle_map):
    """Check if line between p1 and p2 is obstacle-free (Bresenham's algorithm)."""
    x0, y0 = p1
    x1, y1 = p2
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        # Check for obstacle
        if obstacle_map[x0, y0] == 1:
            return False
        
        if x0 == x1 and y0 == y1:
            break
        
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    
    return True
```

**Complexity Analysis:**
- Time: $O(|E| \log |V|)$ where $|V|$ is number of nodes, $|E|$ edges
- Space: $O(|V|)$ for storing g_score, f_score, came_from
- For grid: $|V| = O(w \cdot h)$, $|E| = O(8 \cdot w \cdot h)$
- Overall: $O(wh \log(wh))$

---

### A.4 Dubins Path Planning

#### Mathematical Formulation

Dubins paths are shortest paths for vehicles with minimum turning radius constraint.

**State Space:**

$$
q = (x, y, \theta) \in \mathbb{R}^2 \times S^1
$$

**Path Types:** 6 canonical paths

$$
\{LSL, LSR, RSL, RSR, RLR, LRL\}
$$

Where:
- $L$: Left turn (counterclockwise)
- $R$: Right turn (clockwise)
- $S$: Straight segment

**Path Length:**

$$
L(q_{\text{start}}, q_{\text{goal}}, \rho) = \min_{p \in \mathcal{P}} \ell(p)
$$

Where:
- $\rho$: Minimum turning radius
- $\mathcal{P}$: Set of 6 canonical paths
- $\ell(p)$: Length of path $p$

**Circle Centers:**

$$
\begin{aligned}
C_L &= (x + \rho \sin\theta, y - \rho \cos\theta) \quad \text{(Left circle)} \\
C_R &= (x - \rho \sin\theta, y + \rho \cos\theta) \quad \text{(Right circle)}
\end{aligned}
$$

**LSL Path Construction:**

1. **Circle-to-Circle Tangent:**

$$
\begin{aligned}
d &= \|C_{L,1} - C_{L,2}\| \\
\alpha &= \arctan2(C_{L,2,y} - C_{L,1,y}, C_{L,2,x} - C_{L,1,x})
\end{aligned}
$$

2. **Arc Lengths:**

$$
\begin{aligned}
\ell_1 &= \text{mod}(\alpha - \theta_1, 2\pi) \\
\ell_2 &= d \\
\ell_3 &= \text{mod}(\theta_2 - \alpha, 2\pi)
\end{aligned}
$$

3. **Total Length:**

$$
\ell_{\text{LSL}} = \rho(\ell_1 + \ell_3) + \ell_2
$$

#### Pseudocode

```python
def dubins_path(start, goal, turning_radius):
    """
    Compute shortest Dubins path.
    
    Args:
        start: (x, y, theta) start configuration
        goal: (x, y, theta) goal configuration
        turning_radius: Minimum turning radius (meters)
    
    Returns:
        Path type, length, and waypoints
    """
    x1, y1, theta1 = start
    x2, y2, theta2 = goal
    rho = turning_radius
    
    # Normalize distance by turning radius
    dx = (x2 - x1) / rho
    dy = (y2 - y1) / rho
    d = np.sqrt(dx**2 + dy**2)
    
    # Normalize angles
    alpha = np.arctan2(dy, dx)
    theta1_norm = mod2pi(theta1)
    theta2_norm = mod2pi(theta2)
    
    # Compute all 6 path types
    paths = []
    
    # LSL
    length_lsl = compute_lsl(alpha, d, theta1_norm, theta2_norm)
    if length_lsl is not None:
        paths.append(('LSL', length_lsl * rho))
    
    # LSR
    length_lsr = compute_lsr(alpha, d, theta1_norm, theta2_norm)
    if length_lsr is not None:
        paths.append(('LSR', length_lsr * rho))
    
    # RSL
    length_rsl = compute_rsl(alpha, d, theta1_norm, theta2_norm)
    if length_rsl is not None:
        paths.append(('RSL', length_rsl * rho))
    
    # RSR
    length_rsr = compute_rsr(alpha, d, theta1_norm, theta2_norm)
    if length_rsr is not None:
        paths.append(('RSR', length_rsr * rho))
    
    # RLR
    length_rlr = compute_rlr(alpha, d, theta1_norm, theta2_norm)
    if length_rlr is not None:
        paths.append(('RLR', length_rlr * rho))
    
    # LRL
    length_lrl = compute_lrl(alpha, d, theta1_norm, theta2_norm)
    if length_lrl is not None:
        paths.append(('LRL', length_lrl * rho))
    
    if not paths:
        return None  # No valid path
    
    # Select shortest path
    path_type, path_length = min(paths, key=lambda x: x[1])
    
    # Generate waypoints
    waypoints = generate_dubins_waypoints(start, goal, path_type, turning_radius)
    
    return path_type, path_length, waypoints

def compute_lsl(alpha, d, theta1, theta2):
    """Compute LSL path length."""
    p_squared = 2 + d**2 - 2*np.cos(alpha - theta1) + 2*d*(np.sin(theta1) - np.sin(alpha))
    
    if p_squared < 0:
        return None
    
    p = np.sqrt(p_squared)
    t = mod2pi(-theta1 + np.arctan2(-np.cos(alpha) + np.cos(theta1), d + np.sin(alpha) - np.sin(theta1)))
    q = mod2pi(-alpha + theta2 + np.arctan2(-np.cos(alpha) + np.cos(theta1), d + np.sin(alpha) - np.sin(theta1)))
    
    return t + p + q

def compute_rsr(alpha, d, theta1, theta2):
    """Compute RSR path length."""
    p_squared = 2 + d**2 - 2*np.cos(alpha - theta1) - 2*d*(np.sin(theta1) - np.sin(alpha))
    
    if p_squared < 0:
        return None
    
    p = np.sqrt(p_squared)
    t = mod2pi(theta1 - np.arctan2(np.cos(alpha) - np.cos(theta1), d - np.sin(alpha) + np.sin(theta1)))
    q = mod2pi(alpha - theta2 - np.arctan2(np.cos(alpha) - np.cos(theta1), d - np.sin(alpha) + np.sin(theta1)))
    
    return t + p + q

def compute_lsr(alpha, d, theta1, theta2):
    """Compute LSR path length."""
    p_squared = -2 + d**2 + 2*np.cos(alpha - theta1) + 2*d*(np.sin(theta1) + np.sin(alpha))
    
    if p_squared < 0:
        return None
    
    p = np.sqrt(p_squared)
    t = mod2pi(-theta1 + np.arctan2(np.cos(alpha) + np.cos(theta1), d - np.sin(alpha) - np.sin(theta1)) - np.arctan2(2, p))
    q = mod2pi(-alpha + theta2 - np.arctan2(np.cos(alpha) + np.cos(theta1), d - np.sin(alpha) - np.sin(theta1)) + np.arctan2(2, p))
    
    return t + p + q

def compute_rsl(alpha, d, theta1, theta2):
    """Compute RSL path length."""
    p_squared = -2 + d**2 + 2*np.cos(alpha - theta1) - 2*d*(np.sin(theta1) + np.sin(alpha))
    
    if p_squared < 0:
        return None
    
    p = np.sqrt(p_squared)
    t = mod2pi(theta1 - np.arctan2(-np.cos(alpha) - np.cos(theta1), d + np.sin(alpha) + np.sin(theta1)) + np.arctan2(2, p))
    q = mod2pi(alpha - theta2 + np.arctan2(-np.cos(alpha) - np.cos(theta1), d + np.sin(alpha) + np.sin(theta1)) - np.arctan2(2, p))
    
    return t + p + q

def compute_rlr(alpha, d, theta1, theta2):
    """Compute RLR path length."""
    tmp = (6 - d**2 + 2*np.cos(alpha - theta1) + 2*d*(np.sin(theta1) - np.sin(alpha))) / 8
    
    if abs(tmp) > 1:
        return None
    
    p = mod2pi(2*np.pi - np.arccos(tmp))
    t = mod2pi(theta1 - np.arctan2(np.cos(alpha) - np.cos(theta1), d - np.sin(alpha) + np.sin(theta1)) + p/2)
    q = mod2pi(theta1 - theta2 - t + p)
    
    return t + p + q

def compute_lrl(alpha, d, theta1, theta2):
    """Compute LRL path length."""
    tmp = (6 - d**2 + 2*np.cos(alpha - theta1) - 2*d*(np.sin(theta1) - np.sin(alpha))) / 8
    
    if abs(tmp) > 1:
        return None
    
    p = mod2pi(2*np.pi - np.arccos(tmp))
    t = mod2pi(-theta1 + np.arctan2(-np.cos(alpha) + np.cos(theta1), d + np.sin(alpha) - np.sin(theta1)) + p/2)
    q = mod2pi(theta2 - theta1 - t + p)
    
    return t + p + q

def mod2pi(angle):
    """Normalize angle to [0, 2π)."""
    return angle % (2 * np.pi)

def generate_dubins_waypoints(start, goal, path_type, rho, step=1.0):
    """Generate waypoints along Dubins path."""
    waypoints = [start[:2]]  # Start with (x, y)
    
    x, y, theta = start
    
    for segment in path_type:
        if segment == 'L':
            # Left turn
            waypoints.extend(generate_arc(x, y, theta, rho, 'L', step))
        elif segment == 'R':
            # Right turn
            waypoints.extend(generate_arc(x, y, theta, rho, 'R', step))
        elif segment == 'S':
            # Straight
            waypoints.extend(generate_straight(x, y, theta, goal, step))
    
    waypoints.append(goal[:2])
    return waypoints
```

**Complexity Analysis:**
- Computing 6 path lengths: $O(1)$ each, $O(1)$ total
- Selecting minimum: $O(1)$
- Generating waypoints: $O(L/\delta)$ where $L$ is path length, $\delta$ is step size
- Overall: $O(L/\delta)$

---

### A.5 Coverage Path Planning (Lawnmower Pattern)

#### Mathematical Formulation

**Problem:** Cover rectangular area $A = [0, W] \times [0, H]$ with sensor footprint width $w$.

**Optimal Spacing:**

$$
\lambda = w \cdot (1 - \text{overlap})
$$

Where overlap = 0.2 (20% overlap for reliability)

**Number of Passes:**

$$
N = \lceil H / \lambda \rceil
$$

**Waypoints (Boustrophedon pattern):**

$$
\mathbf{p}_i = \begin{cases}
(0, i \cdot \lambda) & \text{if } i \text{ even} \\
(W, i \cdot \lambda) & \text{if } i \text{ odd}
\end{cases}
$$

For $i = 0, 1, \ldots, N-1$

**Total Path Length:**

$$
L_{\text{total}} = W \cdot N + \lambda \cdot (N-1)
$$

**Coverage Time:**

$$
T_{\text{coverage}} = \frac{L_{\text{total}}}{v} + t_{\text{turn}} \cdot (N-1)
$$

Where:
- $v$: UAV cruise speed
- $t_{\text{turn}}$: Time for 180° turn

#### Pseudocode

```python
def lawnmower_coverage_pattern(area_bounds, sensor_width, overlap=0.2):
    """
    Generate lawnmower coverage pattern for rectangular area.
    
    Args:
        area_bounds: (x_min, y_min, x_max, y_max)
        sensor_width: Width of sensor footprint (meters)
        overlap: Overlap fraction (0.0 - 0.5)
    
    Returns:
        List of waypoints [(x, y), ...]
    """
    x_min, y_min, x_max, y_max = area_bounds
    
    # Calculate spacing between passes
    spacing = sensor_width * (1 - overlap)
    
    # Calculate number of passes needed
    height = y_max - y_min
    num_passes = int(np.ceil(height / spacing))
    
    # Generate waypoints (boustrophedon pattern)
    waypoints = []
    
    for i in range(num_passes):
        y = y_min + i * spacing
        
        if i % 2 == 0:
            # Even pass: left to right
            waypoints.append((x_min, y))
            waypoints.append((x_max, y))
        else:
            # Odd pass: right to left
            waypoints.append((x_max, y))
            waypoints.append((x_min, y))
    
    return waypoints

def spiral_coverage_pattern(center, radius, sensor_width, overlap=0.2):
    """
    Generate spiral coverage pattern (Archimedean spiral).
    
    Args:
        center: (x, y) center of spiral
        radius: Maximum radius
        sensor_width: Width of sensor footprint
        overlap: Overlap fraction
    
    Returns:
        List of waypoints
    """
    spacing = sensor_width * (1 - overlap)
    
    # Archimedean spiral: r = a * theta
    a = spacing / (2 * np.pi)
    
    # Maximum angle
    theta_max = radius / a
    
    # Generate waypoints
    waypoints = []
    theta = 0
    d_theta = 0.1  # Angular step
    
    while theta <= theta_max:
        r = a * theta
        x = center[0] + r * np.cos(theta)
        y = center[1] + r * np.sin(theta)
        waypoints.append((x, y))
        theta += d_theta
    
    return waypoints

def sector_scan_pattern(center, radius, sensor_fov, num_sectors):
    """
    Generate sector scan pattern for circular area.
    
    Args:
        center: (x, y) center of area
        radius: Scan radius
        sensor_fov: Sensor field of view (radians)
        num_sectors: Number of sectors to divide circle
    
    Returns:
        List of waypoints
    """
    waypoints = [center]
    
    sector_angle = 2 * np.pi / num_sectors
    
    for i in range(num_sectors):
        angle = i * sector_angle
        
        # Waypoint at sector edge
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        waypoints.append((x, y))
        
        # Return to center
        waypoints.append(center)
    
    return waypoints

def calculate_coverage_metrics(waypoints, sensor_width, area_polygon):
    """
    Calculate coverage metrics for given path.
    
    Args:
        waypoints: List of (x, y) waypoints
        sensor_width: Sensor footprint width
        area_polygon: Shapely Polygon of area to cover
    
    Returns:
        Dict with coverage percentage, path length, time estimate
    """
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union
    
    # Create sensor footprints along path
    footprints = []
    path_length = 0
    
    for i in range(len(waypoints) - 1):
        p1 = waypoints[i]
        p2 = waypoints[i + 1]
        
        # Path length
        segment_length = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        path_length += segment_length
        
        # Create rectangular footprint along segment
        line = LineString([p1, p2])
        footprint = line.buffer(sensor_width / 2, cap_style=2)  # Flat cap
        footprints.append(footprint)
    
    # Union all footprints
    total_coverage = unary_union(footprints)
    
    # Calculate covered area
    covered_area = total_coverage.intersection(area_polygon).area
    total_area = area_polygon.area
    coverage_percentage = (covered_area / total_area) * 100
    
    # Estimate time (assuming 15 m/s cruise speed, 5s per turn)
    cruise_speed = 15  # m/s
    turn_time = 5  # seconds
    num_turns = len(waypoints) - 2
    
    flight_time = path_length / cruise_speed + num_turns * turn_time
    
    return {
        'coverage_percentage': coverage_percentage,
        'path_length': path_length,
        'flight_time': flight_time,
        'waypoint_count': len(waypoints)
    }
```

**Complexity Analysis:**
- Waypoint generation: $O(N)$ where $N$ is number of passes
- Coverage validation: $O(N \cdot K)$ where $K$ is polygon complexity
- Overall: $O(N \cdot K)$

---

### A.6 Bayesian Sensor Fusion

#### Mathematical Formulation

Fuse confidence scores from multiple sensors using Bayesian inference.

**Prior Probability:**

$$
P(T) = p_{\text{prior}}
$$

**Likelihood for Sensor $i$:**

$$
P(D_i | T) = c_i \quad \text{(detection confidence)}
$$

$$
P(D_i | \neg T) = \alpha_i \quad \text{(false positive rate)}
$$

**Posterior (Single Sensor):**

$$
P(T | D_i) = \frac{P(D_i | T) \cdot P(T)}{P(D_i | T) \cdot P(T) + P(D_i | \neg T) \cdot P(\neg T)}
$$

**Multi-Sensor Fusion (Independent Sensors):**

$$
P(T | D_1, D_2, \ldots, D_n) = \frac{\prod_{i=1}^n P(D_i | T) \cdot P(T)}{\prod_{i=1}^n P(D_i | T) \cdot P(T) + \prod_{i=1}^n P(D_i | \neg T) \cdot P(\neg T)}
$$

**Weighted Fusion:**

$$
P_{\text{fused}} = \frac{\sum_{i=1}^n w_i \cdot c_i}{\sum_{i=1}^n w_i}
$$

Where $w_i$ are sensor reliability weights.

#### Pseudocode

```python
def bayesian_sensor_fusion(sensor_confidences, sensor_weights=None, prior=0.1):
    """
    Fuse multiple sensor detections using Bayesian inference.
    
    Args:
        sensor_confidences: List of confidence scores [c1, c2, ...]
        sensor_weights: Optional reliability weights [w1, w2, ...]
        prior: Prior probability of threat
    
    Returns:
        Fused confidence score
    """
    if not sensor_confidences:
        return prior
    
    if sensor_weights is None:
        # Default: equal weights
        sensor_weights = [1.0] * len(sensor_confidences)
    
    # Normalize weights
    total_weight = sum(sensor_weights)
    sensor_weights = [w / total_weight for w in sensor_weights]
    
    # Bayesian fusion
    # P(T|D1,D2,...,Dn) ∝ P(D1,D2,...,Dn|T) * P(T)
    
    # Assume independent sensors
    likelihood_threat = 1.0
    likelihood_no_threat = 1.0
    
    for conf, weight in zip(sensor_confidences, sensor_weights):
        # P(Di|T) = confidence
        likelihood_threat *= (conf ** weight)
        
        # P(Di|¬T) = false positive rate (assume 0.1)
        fpr = 0.1
        likelihood_no_threat *= (fpr ** weight)
    
    # Posterior
    numerator = likelihood_threat * prior
    denominator = likelihood_threat * prior + likelihood_no_threat * (1 - prior)
    
    posterior = numerator / denominator if denominator > 0 else prior
    
    return posterior

def dempster_shafer_fusion(beliefs):
    """
    Fuse beliefs using Dempster-Shafer theory.
    
    Args:
        beliefs: List of belief structures
                 Each belief: {'threat': p_threat, 'safe': p_safe, 'unknown': p_unknown}
    
    Returns:
        Combined belief structure
    """
    if not beliefs:
        return {'threat': 0, 'safe': 0, 'unknown': 1}
    
    # Start with first belief
    combined = beliefs[0].copy()
    
    # Combine with each subsequent belief
    for belief in beliefs[1:]:
        combined = combine_beliefs_ds(combined, belief)
    
    return combined

def combine_beliefs_ds(belief1, belief2):
    """Combine two beliefs using Dempster's rule of combination."""
    # Compute conflict
    conflict = (
        belief1['threat'] * belief2['safe'] +
        belief1['safe'] * belief2['threat']
    )
    
    if conflict >= 1:
        # Total conflict - cannot combine
        return belief1
    
    k = 1 / (1 - conflict)  # Normalization factor
    
    combined = {
        'threat': k * (
            belief1['threat'] * belief2['threat'] +
            belief1['threat'] * belief2['unknown'] +
            belief1['unknown'] * belief2['threat']
        ),
        'safe': k * (
            belief1['safe'] * belief2['safe'] +
            belief1['safe'] * belief2['unknown'] +
            belief1['unknown'] * belief2['safe']
        ),
        'unknown': k * belief1['unknown'] * belief2['unknown']
    }
    
    return combined

def temporal_fusion(current_confidence, history, decay_factor=0.9):
    """
    Fuse current detection with temporal history.
    
    Args:
        current_confidence: Current frame confidence
        history: List of previous confidences (most recent first)
        decay_factor: Temporal decay (0-1)
    
    Returns:
        Temporally fused confidence
    """
    if not history:
        return current_confidence
    
    # Weighted average with exponential decay
    weights = [decay_factor ** i for i in range(len(history) + 1)]
    confidences = [current_confidence] + history
    
    weighted_sum = sum(w * c for w, c in zip(weights, confidences))
    weight_sum = sum(weights)
    
    return weighted_sum / weight_sum
```

**Complexity Analysis:**
- Bayesian fusion: $O(n)$ for $n$ sensors
- Dempster-Shafer: $O(n^2)$ for $n$ beliefs
- Temporal fusion: $O(h)$ for history length $h$

---

## Key Takeaways

✅ **YOLOv8**: Single-stage detection with CIoU loss, NMS post-processing, $O(HW + N^2)$ complexity  
✅ **Kalman Filter**: Optimal linear estimator for tracking, Hungarian assignment for multi-object, $O(N^3)$ complexity  
✅ **A* Pathfinding**: Optimal with admissible heuristic, $O(wh \log(wh))$ on grid  
✅ **Dubins Paths**: Shortest paths with turning constraints, 6 canonical types (LSL/LSR/RSL/RSR/RLR/LRL)  
✅ **Coverage Patterns**: Lawnmower (boustrophedon), spiral (Archimedean), sector scan  
✅ **Bayesian Fusion**: Multi-sensor confidence combining with Dempster-Shafer for belief fusion  

---

## Navigation

- **Previous:** [Roadmap to Scale](./ROADMAP_TO_SCALE.md)
- **Next:** [Data & Model Specs (Appendix B)](./APPENDIX_B_DATA_MODELS.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
