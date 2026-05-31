fun main() {
    val nums = listOf(1, 2, 3)
    val total = nums.fold(0) { acc, n -> acc + n }
    println(total)
}
