// Run: python -m lang.cli examples/scopes.cl

fn main(): void {
    {
        let x: int = 1;
        print(x);
    }
    // x is out of scope here; this will cause a runtime error
    print(x);
}

