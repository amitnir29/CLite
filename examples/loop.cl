// Run: python -m lang.cli examples/loop.cl

fn main(): int {
    let x: int = 3;
    while (x) {
        x = x - 1;
    }
    return x;
}

