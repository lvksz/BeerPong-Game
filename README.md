# BeerPong-Game

## Game Rules and Points System

### Ranking System
- Players start at the rank **"Żelazo"** and can advance through the following ranks:  
  **Żelazo, Brąz, Srebro, Złoto, Platyna, Diament, Mistrz**.
- Once a player reaches **"Mistrz"**, they no longer advance.

### Points Calculation
- When a match result is confirmed:
  - A base of **20** points is awarded.
  - An additional **2** points are added for each rank difference between the losing player and the winning player (computed as:  
    2 × (index(lossing rank) - index(winning rank))).
  - The number of remaining cups for the winner is also added.
  - The final bonus (added to the winning player's score and subtracted from the losing player's) is calculated as:  
    **max(20 + (rank difference × 2) + remaining cups, 1)**.
  - If the winning match was played away from home and the winning player's win-streak is less than 3, an extra **+3** points bonus is applied.

### Rank Updates
- A player advances to the next rank when accumulating **150** points, after which **150** points are deducted.
- If a player's points drop below 0, points are adjusted and the player may be demoted to a lower rank.