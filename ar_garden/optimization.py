import numpy as np
from typing import List, Tuple
from .models import FieldImage, PlantType, UserPlantSelection

def optimize_plant_placement(field: FieldImage, plant_types: List[PlantType]) -> List[Tuple[float, float, int, float]]:
    """
    Optimize plant placement using a grid-based approach with spacing constraints
    Returns: List of (x, y, plant_type_id, rotation) tuples
    """
    # Convert field dimensions to grid
    grid_size = 0.5  # 0.5m grid cells
    grid_width = int(field.width / grid_size)
    grid_length = int(field.length / grid_size)
    
    # Initialize occupation grid
    occupation_grid = np.zeros((grid_width, grid_length))
    
    # Get existing plants
    existing_plants = UserPlantSelection.objects.filter(field=field)
    for plant in existing_plants:
        x_grid = int(plant.x_position / grid_size)
        y_grid = int(plant.y_position / grid_size)
        radius = int(plant.plant.min_spacing / grid_size)
        mark_occupied_area(occupation_grid, x_grid, y_grid, radius)
    
    # Optimize placement for new plants
    placements = []
    for plant_type in plant_types:
        spacing = int(plant_type.min_spacing / grid_size)
        n_plants = estimate_plant_count(grid_width, grid_length, spacing)
        
        for _ in range(n_plants):
            position = find_best_position(occupation_grid, spacing)
            if position:
                x_grid, y_grid = position
                # Convert grid positions back to meters
                x_meters = x_grid * grid_size
                y_meters = y_grid * grid_size
                rotation = np.random.uniform(0, 360)
                placements.append((x_meters, y_meters, plant_type.id, rotation))
                mark_occupied_area(occupation_grid, x_grid, y_grid, spacing)
    
    return placements

def mark_occupied_area(grid: np.ndarray, x: int, y: int, radius: int):
    """Mark the area around a plant as occupied"""
    height, width = grid.shape
    for i in range(max(0, x - radius), min(width, x + radius + 1)):
        for j in range(max(0, y - radius), min(height, y + radius + 1)):
            if np.sqrt((i - x)**2 + (j - y)**2) <= radius:
                grid[i, j] = 1

def find_best_position(grid: np.ndarray, spacing: int) -> Tuple[int, int]:
    """Find the best position for a new plant"""
    height, width = grid.shape
    min_interference = float('inf')
    best_position = None
    
    for x in range(0, width, spacing):
        for y in range(0, height, spacing):
            if grid[x, y] == 0:
                interference = calculate_interference(grid, x, y, spacing)
                if interference < min_interference:
                    min_interference = interference
                    best_position = (x, y)
    
    return best_position

def calculate_interference(grid: np.ndarray, x: int, y: int, spacing: int) -> float:
    """Calculate how much a plant at (x,y) would interfere with others"""
    height, width = grid.shape
    interference = 0
    radius = spacing // 2
    
    for i in range(max(0, x - radius), min(width, x + radius + 1)):
        for j in range(max(0, y - radius), min(height, y + radius + 1)):
            if grid[i, j] == 1:
                distance = np.sqrt((i - x)**2 + (j - y)**2)
                if distance < spacing:
                    interference += 1 - (distance / spacing)
    
    return interference

def estimate_plant_count(width: int, length: int, spacing: int) -> int:
    """Estimate how many plants can fit in the area"""
    area = width * length
    plant_area = spacing * spacing * np.pi
    return int(area / (plant_area * 2))  # Using 50% of theoretical maximum 