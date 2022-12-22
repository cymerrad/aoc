import scala.io.Source
import scala.util.parsing.combinator._
import Ordering.Implicits._
import scala.util.control.Breaks._

object Main {
  def main(args: Array[String]): Unit = {
    val cave = CaveMap(InputResource.input_lines)
    val turns = cave.simulate()
    println(cave)
    println(s"Simulation took $turns turns")

    val cave2 = CaveMapBottomFloor(InputResource.input_lines, 150)
    val turns2 = cave2.simulate()
    println(cave2)
    println(s"Simulation 2 took $turns2 turns")
    // 3059 is too low
  }
}

enum Box(val value: Char, var solid: Boolean = false):
  case Air extends Box('.')
  case Sand extends Box('o')
  case Wall extends Box('#', true)
  case Source extends Box('+')

/** (iy, ix) ~ (row,col)
  */
type Idx = (Int, Int)

class CaveMap(
    val lines: List[String],
    noInit: Boolean = false
) {
  val p = LineParser
  var data: Array[Array[Box]] = Array.ofDim[Box](0, 0)
  var sandSource: Idx = (0, 0)

  var minLeft = 500
  var maxRight = 500
  var maxHeight = 0

  val setsOfLines = for line <- lines yield {
    val l = p.main(line)
    for (x, y) <- l do {
      minLeft = minLeft min x
      maxRight = maxRight max x
      maxHeight = maxHeight max y
    }
    l
  }
  var height: Int = maxHeight + 1
  var width: Int = maxRight - minLeft + 1
  var startX: Int = minLeft

  def init() = {
    println(s"Init { height:$height width:$width startX:$startX }")

    data = Array.ofDim[Box](height, width)
    for (iy <- 0 until height; ix <- 0 until width) {
      setBox((iy, ix), Box.Air)
    }

    val setsOfIdxs = for line <- setsOfLines yield line.map(pointToIdx)

    for idxs <- setsOfIdxs do {
      val pairs =
        for ind <- 0 until idxs.length - 1
        yield (idxs(ind), idxs(ind + 1))

      for (p1, p2) <- pairs do {
        val xsRange = (p1(1), p2(1))
        val ysRange = (p1(0), p2(0))
        val (loX, hiX) = xsRange min xsRange.swap
        val (loY, hiY) = ysRange min ysRange.swap
        for
          iy <- loY to hiY
          ix <- loX to hiX
        do {
          try {
            setBox((iy, ix), Box.Wall)
          } catch {
            case ex: ArrayIndexOutOfBoundsException => {
              println(s"OOB: ($iy, $ix); xs: $xsRange; ys: $ysRange")
              println(pairs)
              throw ex
            }
          }

        }
      }
    }

    sandSource = pointToIdx((500, 0))
    setBox(sandSource, Box.Source)
  }

  if (!noInit) init()

  /** Converts input data point (like (500,0)) to a pair of matrix indices.
    *
    * @param point
    *   Ex. (500,0)
    * @return
    *   Ex. (0, 6) ~ (Y, X)
    */
  def pointToIdx(point: (Int, Int)): Idx = (point(1), point(0) - startX)

  def getBox(pos: Idx): Option[Box] = {
    try {
      Some(data(pos(0))(pos(1)))
    } catch {
      case ex: ArrayIndexOutOfBoundsException => None
    }
  }
  def setBox(pos: Idx, box: Box) = data(pos(0))(pos(1)) = box

  /** @param from
    * @param to
    * @return
    *   Resultant move
    */
  def move(from: Idx, to: Idx): Option[Idx] = {
    val moving = getBox(from)
    try {
      moving match
        case None => None
        case Some(value) => {
          setBox(from, Box.Air)
          setBox(to, value)
          Some(to)
        }
    } catch {
      case ex: ArrayIndexOutOfBoundsException => None
    }
  }

  /** Calculates step for a box, returns progress of focus.
    *
    * @param cur
    *   Current position
    * @return
    *   Resultant of a step: new position or None
    */
  def step1(cur: Idx): Option[Idx] = {
    val (iy, ix) = cur
    val down = (iy + 1, ix)
    getBox(cur) match
      case Some(Box.Sand) => {
        getBox(down) match
          case Some(Box.Air) => move(cur, down)
          case None          => None
          case _ => {
            val left = (iy + 1, ix - 1)
            getBox(left) match
              case Some(Box.Air) => move(cur, left)
              case None          => None
              case _ => {
                val right = (iy + 1, ix + 1)
                getBox(right) match
                  case Some(Box.Air) => move(cur, right)
                  case None          => None
                  case _             => Some(cur)
              }
          }
      }
      // case Some(Box.Source) => {
      //   getBox(down) match
      //     case Some(Box.Air) => {
      //       // spawn sand
      //       setBox(down, Box.Sand)
      //       Some(down)
      //     }
      //     case Some(Box.Sand) => {
      //       // spawn sand
      //     }
      //     case None => None
      //     case _    => Some(cur)
      // }
      case _ => Some(cur)

  }

  def dropSand(): Option[Idx] = {
    getBox(sandSource) match
      case Some(Box.Source) => {
        val (iy, ix) = sandSource
        val down = (iy + 1, ix)
        val left = (iy + 1, ix - 1)
        val right = (iy + 1, ix + 1)
        if (
          getBox(down) == Some(Box.Sand)
          && getBox(left) == Some(Box.Sand)
          && getBox(right) == Some(Box.Sand)
        ) {
          setBox(sandSource, Box.Sand)
          // return Some(sandSource)
          return None
        }

        setBox(sandSource, Box.Sand)
        val finalPos = stepUntillStill(sandSource)
        setBox(sandSource, Box.Source)
        finalPos
      }
      case Some(Box.Sand) => None // full pile of sand
      case _              => None // should throw or sth

  }

  def stepUntillStill(start: Idx): Option[Idx] = {
    step1(start) match
      case None => None // out of bounds
      case Some(newValue) =>
        if (newValue != start) stepUntillStill(newValue) else Some(newValue)
  }

  def simulate(turn: Int = 0): Option[Int] = {
    val ceiling = 40_000
    // var turns = 0
    // breakable {
    //   for turn <- 0 until ceiling do {
    //     turns += 1
    //     dropSand() match
    //       case None        => break
    //       case Some(value) => {}
    //   }
    // }
    // Some(turns - 1)
    if (turn > ceiling) None
    else {
      dropSand() match
        case None => Some(turn)
        case Some(value) =>
          simulate(turn + 1)
    }

  }

  override def toString(): String =
    data.map(row => row.map(_.value).mkString("")).mkString("\n")
}

class CaveMapBottomFloor(lines: List[String], padding: Int = 5)
    extends CaveMap(lines, true) {

  height += 2
  width += (2 * padding)
  startX -= padding

  init()
  updateBottomRow()

  def updateBottomRow() = {
    for ind <- 0 until width do {
      setBox((height - 1, ind), Box.Wall)
    }
  }

}

object LineParser extends RegexParsers {
  def tuple = """(\d+),(\d+)""".r ^^ { s =>
    {
      val strTup = s.splitAt(s.indexOf(","))
      (strTup(0).toInt, strTup(1).toInt)
    }
  }

  def arrow = "->"
  def comma = ","
  def number = """\d+""".r
  def tup = number ~ comma ~ number
  def line = rep1sep(tup, arrow)

  def main(input: String) = {
    parse(line, input) match {
      case Success(matched, _) => {
        for {
          m <- matched
        } yield {
          m match {
            case _1 ~ _2 =>
              _1 match {
                case _11 ~ _12 =>
                  (_11.toInt, _2.toInt)
              }
          }
        }
      }
      case Failure(msg, _) => { println(s"FAILURE: $msg"); Nil }
      case Error(msg, _)   => { println(s"ERROR: $msg"); Nil }

    }
  }
}

class InputResource(val test: Boolean = false):
  import InputResource.*
  val data = if test then { test_lines }
  else { input_lines }
  val parser = LineParser

object InputResource:
  val input_r = Source.fromResource("input.txt")
  val input_lines = input_r.getLines().toList
  val test_r = Source.fromResource("test.txt")
  val test_lines = test_r.getLines().toList
