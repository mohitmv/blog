---
layout: post
title: "Dangerous Usage of GTest's EXPECT macro"

---

GTest is a unit testing library by Google. It provides easy to use macros for enforcing expectation in unit tests. Commonly used macros are of kind `EXPECT_*` and `ASSERT_*`, example: `ASSERT_TRUE(c)`, `EXPECT_TRUE(c)`, `EXPECT_EQ(a, b)`, `ASSERT_EQ(a, b)`.

The difference between EXPECT and ASSERT macros is that when ASSERT fails, the tests is marked "Failed" and program flow exits from that particular test. However when EXPECT fails, the test is marked "Failed" but the program flow doesn't exit instead it continues to next step. Hence EXPECT can be used for reporting all the failing expectations. However ASSERT can only report the first failing expectation.

Hence there is great incentive in using EXPECT as much as we can.

**However using EXPECT macro at wrong places, can land us in serious troubles.** It expose the possibility/vulnerability of something **being broken** and still **tests passing**.

### Consider this simple program and it's unit test:

{% highlight c++ %}

// a.h
std::vector<int> FetchTwoValues(NetworkSocket& socket);

// a.cpp
std::vector<int> FetchTwoValues(NetworkSocket& socket) {
  return {socket.Fetch(), socket.Fetch()};
}

// a_test.cpp
TEST(A, Basic) {
  auto socket = MockSocket();
  std::vector<int> values = FetchTwoValues(socket);
  EXPECT_TRUE(values.size() >= 2);
  EXPECT_TRUE(0 == values[0]);
  EXPECT_TRUE(0 == values[1]);
}

{% endhighlight %}


At the high level, this test appears correct.

Recall the definition of gtest's EXPECT_ macro: ( Ignoring the debug-message-streaming and other stuff for simplicity)

{% highlight c++ %}

#define EXPECT_TRUE(c) if (!(c)) { this->failed = true; }
#define ASSERT_TRUE(c) if (!(c)) { this->failed = true; return; }

{% endhighlight %}


### Let's there is a bug in `FetchTwoValues`

Let there is a bug in `FetchTwoValues` method and it returns an empty vector.

The `EXPECT_TRUE(values.size() >= 2)` will fail, and test will continue to next EXPECT_TRUE, which will be an illegal dereferencing (UB), and the test program might crash instead of failing, even before attempting all other test cases in this test file.
but that crash is not a big problem because the crash will help us notice the problem and we can figure out. That is not the real problem.

The real problem is - the test might not crash. The real problem is, test can still succeed even if `FetchTwoValues` returns an empty vector. That is way too unintuitive and dangerous thing..

The reason behind this unintuitive behaviour is UB. A program is not "defined to crash" on a UB. A program is defined to do anything of compiler's choice on UB. In fact this "might-not-crash" event might not happen all the time, all the places. It can happen nondeterministically and occasionally, leaving no room for us to debug.

### How does it succeed when `FetchTwoValues` returns an empty vector


First of all, the compiler don't know the definition of `FetchTwoValues` when compiling `a_test.cpp`. Secondly it notices a memory access `values[0]`, `values[1]` at the next step. At this step compiler's static analysis (compile time analysis) can deduce that `values.size() >= 2`, assuming that memory access is not illegal (UB o.w.), and (Note that compiler have access to the `std::vector`'s implementation in this translation unit).

Hence a compiler can replace `values.size() >= 2` by `true` without violating as-if rule of C++.

Hence it can remove the `EXPECT_TRUE(values.size() >= 2)` macro at compile time.

A sufficiently optimized compiler can do following compile time reasoning about the removal of `EXPECT_TRUE(values.size() >= 2)` :

Case-1 `values.size() >= 2` then it's obviously safe to remove this macro.

Case-2 `values.size() < 2` then `values[1]` is illegal access, hence this program will have UB if `values[1]` statement is reachable. Note that if a program have UB, then the behaviour *preceding* the first UB instruction is also undefined. Hence compiler have liberty to do anything in that case, including *removing* all the paths which cannot avoid reaching at the UB instruction. i.e. the paths that cannot escape this UB. Hence it's safe to remove the `EXPECT_TRUE(values.size() >= 2)` macro. Note that its guaranteed that this macro is not reachable via any non-UB paths.

When `FetchTwoValues` returns an empty vector, and the next two illegal memory access (`values[0]` and `values[1]`) might continue to return 0 as a garbage value. Hence this test may continue to succeed.

### How to fix this:

To correct the test above, we should use `ASSERT_TRUE(values.size() >= 2)` instead of `EXPECT_TRUE(values.size() >= 2)`.

Note that in case of ASSERT_TRUE, there is indeed an escape path (see `return;` in `ASSERT_TRUE`). Hence compiler cannot trim ASSERT_TRUE at compile time, because there exists a path that goes through ASSERT_TRUE and doesn't have UB in it.


Learn in depth about [Undefined Behaviour](https://mohitmv.github.io/blog/Cpp-Undefined-Behaviour-101/) and their danger.
