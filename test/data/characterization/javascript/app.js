const add = (a, b) => a + b;

function main() {
    const nums = [1, 2, 3];
    console.log(nums.reduce(add, 0));
}

main();
