import matplotlib.pyplot as plt

import ar_math_helper

# Wrap formulas so they return a list of length `count`
formulas = {
    1: ("damage", lambda count: [ar_math_helper.formulas.damage_upgrade(i) for i in range(count)]),
    2: ("firerate", lambda count: [ar_math_helper.formulas.firerate_upgrade(i) for i in range(count)]),
    3: ("b_spd", lambda count: [ar_math_helper.formulas.b_speed_upgrade(i) for i in range(count)]),
}

# Average multiple runs of a selected formula
def get_averaged_data(count, runs, formula_fn):
    if count <= 0:
        raise ValueError("count must be > 0")
    if runs <= 0:
        raise ValueError("runs must be > 0")

    acc = [0.0] * count
    for _ in range(runs):
        data = formula_fn(count)
        if len(data) != count:
            raise ValueError(f"Formula returned {len(data)} points, expected {count}.")
        acc = [a + float(x) for a, x in zip(acc, data)]
    return [a / runs for a in acc]

# Simple line chart display
def show_chart(data, label):
    plt.figure()
    plt.plot(data)
    plt.title(f"Averaged Data - {label}")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    try:
        count = int(input("Enter number of data points per run: "))
        runs = int(input("Enter number of runs to average: "))

        print("Choose a formula:")
        for k, (name, _) in formulas.items():
            print(f"{k} - {name}")
        choice = int(input("Enter number: "))

        if choice not in formulas:
            print("Invalid choice")
        else:
            label, fn = formulas[choice]
            averaged = get_averaged_data(count, runs, fn)
            show_chart(averaged, label)
    except Exception as e:
        print(f"Error: {e}")
