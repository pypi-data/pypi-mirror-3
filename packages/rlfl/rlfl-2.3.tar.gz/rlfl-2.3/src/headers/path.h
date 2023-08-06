/*
	RLFL pathfinding types.

    Copyright (C) 2011

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>

    <jtm@robot.is>
*/
/* Structure for path elements */
typedef struct path_element {
    int x;
    int y;
    int cost;
    int estimate;
    unsigned int state;
    struct path_element* parent;
} path_element;

/* Dijkstra grid */
typedef struct {
	/* Stack of unprocessed nodes */
	path_element ** open;

	/* map of all nodes */
	path_element * nodes;

	/* */
	int top;

	/* Diagonal cost */
	float dcost;

	/* Use estimates */
	bool astar;

	unsigned int cx, cy;
} path_int_t;
path_int_t* PATH;

#define STATE_EMPTY		0
#define STATE_OPEN		1
#define STATE_CLOSED	2

extern void delete_path(void);
