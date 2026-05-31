interface Point {
    x: number;
    y: number;
}

function dist(p: Point): number {
    return Math.sqrt(p.x * p.x + p.y * p.y);
}

console.log(dist({ x: 3, y: 4 }));
