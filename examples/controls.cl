// Run: python -m lang.cli examples/controls.cl

fn main(): int {
    if (true && (1 < 2)) {
        print("branch: then");
        return 1;
    } else {
        print("branch: else");
        return 0;
    }
}

