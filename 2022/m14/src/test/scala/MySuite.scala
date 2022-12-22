// For more information on writing tests, see
// https://scalameta.org/munit/docs/getting-started.html

class MySuite extends munit.FunSuite {
  test("Map prints at all") {
    val cave = CaveMap(InputResource.test_lines)
    val map = cave.toString()
    assert(!map.isEmpty())
  }

  test("24 units of sand have fallen down") {
    val cave = CaveMap(InputResource.test_lines)
    val turns = cave.simulate()

    // for turn <- 0 to 27 do {
    //   cave.stepUntillStill(cave.sandSource)
    //   println(cave)
    // }

    turns match
      case Some(t) => {
        val obtained = t
        val expected = 24
        assertEquals(obtained, expected)
      }
      case None => {
        assert(false)
      }
  }

  test("Second map prints") {
    val cave = CaveMapBottomFloor(InputResource.test_lines)
    val map = cave.toString()
    assert(!map.isEmpty())
  }

  test("93 units of sand have fallen down") {
    val cave = CaveMapBottomFloor(InputResource.test_lines, 15)
    val turns = cave.simulate()
    println(cave)

    // var breakPoint2 = 15
    // var breakPoint1 = 70

    // for turn <- 0 to breakPoint1 do {
    //   cave.stepUntillStill(cave.sandSource)
    //   // println(cave)
    // }

    // for turn <- breakPoint1 to breakPoint2 do {
    //   cave.stepUntillStill(cave.sandSource)
    // }

    // for turn <- breakPoint2 to 93 do {
    //   cave.stepUntillStill(cave.sandSource)
    //   println(cave)
    // }

    turns match
      case Some(t) => {
        val obtained = t
        val expected = 93
        assertEquals(obtained, expected)
      }
      case None => {
        assert(false, "Limit reached")
      }

    assert(false)
  }
}
