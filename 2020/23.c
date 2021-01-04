#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Node {
  struct Node *next;
  // struct Node *prev;
  int value;
};

typedef struct Node node;

const int SENTINEL = -1;
const int MILLION = 1000000;

node *newNode(int value)
{
  node *new = malloc(sizeof(node));
  new->value = value;
  return new;
}

void bindNodes(node *before, node *after)
{
  before->next = after;
  // after->prev = before;
}

node *newList(int elements[9], int doMillion)
{
  node *start = newNode(SENTINEL);


  node *prev = start;
  for (int i = 0; i < 9; i++)
  {
    node *next = newNode(elements[i]);
    bindNodes(prev,next);

    prev = next;
  }

  if (doMillion)
  {
    for (int i = 10; i <= 1000000; i++)
    {
      node *next = newNode(i);
      bindNodes(prev,next);

      prev = next;
    }
  }

  // loop
  // bindNodes(prev, start);

  // loop without a sentinel
  bindNodes(prev, start->next);

  return start->next;
}

node *insertValue(node *before, int value)
{
  node *new = newNode(value);
  node *after = before->next;

  bindNodes(before, new);
  bindNodes(new, after);

  return new;
}

// int removeNode(node *removed)
// {
//   int removedValue = removed->value;
//   //printf("\t\t\t\tremoving %d\n", removedValue);

//   node *before = removed->prev;
//   node *after = removed->next;
//   bindNodes(before, after);

//   free(removed);

//   return removedValue;
// }

int removeAfterNode(node *before)
{
  node *removed = before->next;
  int removedValue = removed->value;

  node *after = removed->next;
  bindNodes(before, after);

  free(removed);

  return removedValue;
}


node *indexValue(node *start, int needle)
{
  // //printf("\t\t\t\tvisiting %d in search for %d\n", start->value, needle);
  while (start->value != needle)
  {
    start = start->next;
  }

  // not using the sentinel so we might loop forever
  // YOLO
  return start;
}

int *getNElements(int N, node *anyNode, int startValue)
{
  node *start = indexValue(anyNode, startValue);
  int *buf = malloc(N * sizeof(int));
  for (int i = 0; i < N; i++)
  {
    buf[i] = start->value;
    start = start->next;
  }

  return buf;
}

int TEST_CASE[9] = {3,8,9,1,2,5,4,6,7};
int TEST_CASE_AFTER_10[9] = {1,9,2,6,5,8,3,7,4};
int TEST_CASE_AFTER_100[9] = {1,6,7,3,8,4,5,2,9};

struct Wheel {
  node *current;
  int maxValue;
};

int xIn3Tuple(int x, int t1, int t2, int t3)
{
  return (x == t1) || (x == t2) || (x == t3);
}

void move(struct Wheel *w)
{
  // node *fourthAfter = w->current->next->next->next->next;
  // int r1 = removeNode(w->current->next);
  // int r2 = removeNode(w->current->next);
  // int r3 = removeNode(w->current->next);
  //printf("Removed (%d, %d, %d); %d -> %d\n", r1,r2,r3, w->current->value, w->current->next->value);

  int r1 = removeAfterNode(w->current);
  int r2 = removeAfterNode(w->current);
  int r3 = removeAfterNode(w->current);

  int label = w->current->value;
  int highestNext = label - 1;
  while (xIn3Tuple(highestNext, r1, r2, r3))
  {
    highestNext--;
  }

  if (highestNext < 1)
  {
    highestNext = w->maxValue;
    //printf("wut %d\n", highestNext);
    while (xIn3Tuple(highestNext, r1, r2, r3))
    {
      highestNext--;
    }
  }

  //printf("Searching for %d\n", highestNext);
  node *destination = indexValue(w->current, highestNext);
  //printf("Destination value %d\n", destination->value);
  insertValue(insertValue(insertValue(destination, r1), r2), r3);

  w->current = w->current->next;
}

void printArray(int *arr, int size)
{
  //printf("[");
  int i = 0;
  for (;i < size - 1; i++)
  {
    //printf("%d, ", arr[i]);
  }
  //printf("%d]\n", arr[i]);
}

struct Wheel *playWheel(int startingValues[9], int moves, int doMillion)
{
  struct Wheel *w = malloc(sizeof(struct Wheel));
  node *start = newList(startingValues, doMillion);
  w->current = start;
  w->maxValue = (!doMillion) ? 9 : MILLION;

  for (int i = 0; i < moves; i++)
  {
    //printf("Current %d\n", w->current->value);

    // int *arr = getNElements(9, w->current, w->current->value);
    //printArray(arr, 9);

    move(w);

    if (i % 1000 == 0) {
      printf("Move %d\n", i);
    }
  }

  // int *arr = getNElements(9, w->current, 1);
  //printArray(arr, 9);

  return w;
}

int REAL_CASE[9] = {1,5,6,7,9,4,8,2,3};

int main(int argc, char const *argv[])
{

  // struct Wheel *w = playWheel(TEST_CASE, 10, 0);
  // int *res = getNElements(9, w->current, 1);
  // int isGood = memcmp(res, TEST_CASE_AFTER_10, 9);
  // printf("Result %d (should be 0)\n", isGood);

  struct Wheel *w = playWheel(REAL_CASE, 10 * MILLION, 1);
  node *one = indexValue(w->current, 1);
  printf("FUCKING POINTLESS LOL\n");
  printf("Next values: %d %d\n", one->next->value, one->next->next->value);

  return 0;
}
