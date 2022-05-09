#ifndef GOL_H
#define GOL_H

#include <inttypes.h>

typedef uint8_t pixel_t;

typedef struct {
    int width, height;
    pixel_t **cells;
} world;

world worlds[2];
world *cur_world, *next_world;

void world_border_timestep(world *old, world *new);
void world_timestep(world *old, world *new);

#endif
