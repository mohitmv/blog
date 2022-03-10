# Cpp Coding Core Guidelines

## Abstract

- This Article is WIP (Work in Progress) yet.
- [What this article is about and what it is not about](#about)
- [What is undefined behaviour (UB) in C++. Why is it dangerous ?](#undefined-behaviour)
- 20 red flags every C++ code reviewer should be aware of
- [Appendix](#appendix)


## About

This article assumes that reader already know C++ at least at basic level and the reader has good understanding of  programming in at least one language.

This article is about the core guidelines of C++ programming in our codebase. If we miss any of these core guidelines, we will face serious consequences in terms or software sanity, software performance, build performance, bug vulnerability etc.

This article talks about design standardization in code base, including file/folder structuring, modularity, design patterns, standardization on function signature, error handling etc. If we miss to comply with design standardization there won't be serious consequence unlike core guidelines, but there will be significant consequence in terms of code readability, code extensibility, elegancy and usability.

This article doesn't talk about line spacing, variable naming etc. These lint guidelines can be read from [google style guideline](https://google.github.io/styleguide/cppguide.html)

## Undefined Behaviour

#### Undefined Behaviour (UB), it's danger and introduction to C++

The introduction to C++ starts with the most important thing about C++, that is Undefined Behaviour. UB exists only in C/C++, or their sibling languages (eg: Rust, Circle etc.), having similar performance goals. UB doesn't exists in most of the programming languages people are aware of - including Java, Python, Perl, Groovy, JavaScript, TypeScript, Bash, Go.

If you are coming from these language to C++, it's very important to understand the UB very well.

For any programming language, there exists a definition of valid program. Given any string made of ascii characters, the string is either defined to be a valid program of that language or not.

Most of the programming languages requires that execution of every valid program should give correct result, and execution/compilation of every illegal program should fail.
Note: here correct result is defined w.r.t intent of the program.
For example, the Java program:
```
public static void main(String[] args) {
  1/0;
}
```
raise exception. and that was the intent. Hence the result (exception) is correct.

and the following Java program is illegal. Hence compilation fails.
```
public public static void main() { }
```

However C/C++ doesn't require that execution/compilation of every illegal program should fail. A program can be illegal and still it can work. Repeat after me - **"A C++ program can be illegal and still work as you wished"**. That's what the danger is.
- An illegal C++ program might stop working tomorrow.
- It might stop working on Friday and Monday but works rest of the week.
- It might work all the time except when you have to demonstrate your App to customers.
- It might stop working if you run it after eating large pizza but works if you run it after eating sandwich.

And, it's **perfectly legal** for a C/C++ compiler to do this with a program. A Java compiler don't have liberty to do this.


C/C++ standard require that execution of every valid program should give correct result, but if the program is illegal then the behaviour is either defined to be diagnosable by compiler or the behaviour is undefined.

If the illegal program is defined to be diagnosable by compiler, any standard compliant compiler is obliged to fail the compilation (Possibly with readable errors). However if a illegal program doesn't fall into definition of diagnosable program, compiler have full liberty to do anything with that program.

For a program with reachable UB, it's legal for a compiler to generate such an executable:
- That gives incorrect output.
- That is an empty executable.
- Whose execution deletes all the data from your disc.
- Whose execution explode and burn the computer.
- Whose execution invoke the API to crash the engine of rocket in which this program is running.

All that is legal for a standard compliant compiler to do.

Humorously, Undefined behaviour is also called "nasal demons". Here is the context:

> The term originally originated from a post by John F. Woods on 2/25/1992 in a discussion on the Usenet group comp.std.c[1]. Mr Woods was attempting to emphasis the fact that undefined behaviour may legally (as far as the standard is concerned) result in the compiler doing just about anything - including but not limited to "having demons fly out of your nose". The aim of the post was to make the point that one cannot put the compiler at fault for input which has no defined behaviour as far as the c standard is concerned.

> References:
- https://accu.org/journals/overload/21/115/maudel_1857/
- https://en.wikichip.org/wiki/nasal_demons
- https://en.wikipedia.org/wiki/Undefined_behavior


So far we have seen the danger of UB. Now the next question is, why did C++ standard give such powerful liberty to compilers ?

The answer is, "Optimizations". C++ Compilers assumes a lot of things due to UB. These assumptions enables optimizations.

Consider the example:

```
int* a = new int[10];
a[20] = 4;
```

This program is writing at illegal memory (UB). Consequence of this program cannot be even measured. This one illegal write can cause this program to delete entire disc. Imagine there were filepath chars written at `a[20]` address, to be used by some other function in this program. This `a[20] = 4` changes that filepath to something, matching with filepath of entire disc. So the other function that was supposed to delete only one file, will end up deleting entire disc.

How java handles it:

Java translate this code into something like:
```
if (20 < a.length) {
  a[20] = 4
} else {
  throw new Exception("Out of Index");
}
```

Which is safe but require an extra `if` check. `C++` cannot afford an extra `if` for every memory read-write. So C++ simply declare illegal memory access a `UB`, so that compiler don't have to check validity of memory and still remain standard compliant.


Note that `C++` is not a programming language that can be learnt by trial and errors. A lot of things are wrong but works. Only way to know if a program is legal or not, is to get it stamped by C++ standard.


C++ standard says, if an instruction with undefined behaviour is reachable in C++ program, the behaviour of entire program is undefined, including the instruction preceding the first occurrence of undefined behaviour.

This statement from C++ standard allows compiler to eliminate the code blocks that has reachable path to UB.

So what do you think would be the output of this program on sufficiently optimised compiler, for argc = 1 and 2 respectively ?

```
int main(int argc, char* argv[]) {
  int *a = nullptr;
  std::cout << "ABC " << argc << std::endl;
  if (argc == 1) {
    std::cout << "DEF" << std::endl;
    std::cout << *a << std::endl;
  }
  std::cout << "GHI" << std::endl;
  return 0;
}
```

Correct Answer:
For argc = 2, it would be `ABC 2` and `GHI` as expected.
For argc = 1, it would be again `ABC 1` and `GHI`. Program might not print `DEF` and might not crash.

Question - How is that happening for argc = 1 case ?

Answer - A sufficiently optimised compiler can eliminate the `if` block while compiling this program.

Question - Why ? isn't compiler violating `as if` rule here ? at least `DEF` should have been printed. nullptr  dereferencing was done after printing `DEF`.

Answer - `as if` rule won't apply here because the behaviour of the program is undefined even for the instruction preceding the nullptr dereferencing. As a choice, compiler didn't print `DEF`. That choice gave the liberty to eliminate away the entire `if` block. Compiler can assume that developer will never involve UB. `if` block has a UB, so compiler can safely assume that condition with the `if` will never be true. (if it does then UB will safeguard compiler).

Question - This is unintuitive and can be very risky in more complex cases

Answer - Yes it is and hence UB is dangerous, because compilers assumes developers will never involve UB.




Another example:

C++ standard says integer overflow of signed integer has undefined behaviour.
i.e. they are saying compiler can assume that for every signed integers `a` and a positive number `b`, 
`a + b > a`. This assumptions allows a lot of compiler optimisations. Note: overflow by arithmetic ops on unsigned integers have well defined semantics.


Consider this program (by @eric.musser in #cpp channel)

```

int main() {
    char buf[50] = "y";
    for (int j = 0; j < 9; ++j) {
        std::cout << (j * 0x20000001) << std::endl;
        if (buf[0] == 'x') break;
    }
}

```
https://godbolt.org/z/bzrbox

It goes in infinite loop.

Why ?

Because it involves undefined behaviour (signed integer overflow). There are two optimisations involved.

First one translates it to:

```
  for (int j = 0; j < 9 * 0x20000001; j += 0x20000001) {
      std::cout << j << std::endl;
      if (buf[0] == 'x') break;
  }
```

Second optimisation reduces `'j < 9 * 0x20000001'` to `true` because RHS is more than INT_MAX. and `j` being an integer cannot be more than INT_MAX.
So that for loop now becomes

for (int j = 0; true; j+=...) {....}


and hence infinite loop.

Moral of the story : Stay away from the 'undefined behaviour'.


Short Quiz

Q1. Does this program have UB ? Explain.

```C++
int x[10];
int& a = x[20];
```

Q2. Does this program have UB ? Explain.

```C++
int main(int argc, char* argv[]) {
  if (argc > argc) {
    int x[10];
    int a = x[20];
  }
}
```

Q3. Does this program have UB ? Explain.

```C++
for (int i = 2; i > 1; i++) {
  std::cout << i << std::endl;
}
```

Q4. Does this program have UB ? Explain.

```C++
for (uint i = 2; i > 1; i++) {
  std::cout << i << std::endl;
}
```

Q5. Does this program have UB ? Explain. What would be output of this program ?

```C++
int x;
x = x * 0;
std::cout << x << std::endl;
```

Q6. Does this program have UB ? Explain. Will assertion fail or no ?

```C++
int a = 4;

void Thread1() {
  a++;
}

void Thread2() {
  int b = a;
  assert(b == 4 || b == 5);
}

```

#### Unspecified Behaviour

Unspecified behaviour is different from undefined behaviour. Presence of reachable **'undefined behaviour'** makes a program illegal. However **'unspecified behaviour'** is not that serious. If value/state of an object is unspecified, it means the object is valid and it's value is one of the valid value from it's value-space, however there is no guarantee which one value.
For example:

```C++
vector<int> v = {10, 20, 30};
auto v2 = std::move(v);
// At this point value of v is unspecified. However it's value is exactly one
// of the possible value of vector<int>.
```

#### Unspecified Evaluation Order

Q7. What should be output of this program ?

```C++
int F() { std::cout << 'F'; return 10; }
int G() { std::cout << 'G'; return 20; }
int main() {
  int x = F() + G();
}
```

As per C++ standard order of evaluation of a function-call argument is unspecified. (Special rule for scalers args).

Hence the output of the program above could either be `FG` or `GF`. However there doesn't exists any other possibility of the output of this program.

Short Quiz

Q8. What would be output of this program, for standard input '15 5 '.

```C++
int k;
std::unordered_map<int, int> a;
std::cin >> k >> a[k];
std::cout << a[k];
```

Q9. What would be output of this program ?

- Option A). Garbage (Unspecified Value)
- Option B). 0
- Option C). UB.
- Option D). 0 if it is single threaded program else garbage.

```C++
int* x = new int;
delete x;
int y = *x;
std::cout << y;
```

Q10. What would be output of this program ?

- Option A). Garbage (Unspecified Value)
- Option B). 0
- Option C). UB.
- Option D). 0 if it is single threaded program else garbage.

```C++
int* x = new int;
int y = *x;
delete x;
std::cout << y;
```


## Core Guidelines

These specific guidelines inherits from [CppCoreGuidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) with emphasis/extension on following points.

1. [[Avoid Memory Leaks] Never use raw pointers except in special cases.](#avoid-memory-leaks)
2. [[Performance] Throw exceptions but never catch them except in special cases.](#performance)
3. [[Avoid Incorrect Binding] Don’t expose global level symbols in headers.](#avoid-incorrect-binding)
4. [Avoid Linker Error] Avoid cyclic dependencies among modules.
5. [[Performance.Alloc] Don’t use unique_ptr as a substitute of std::optional.](#performancealloc)
6. [[Exclusive Ownership] Don’t use shared_ptr unless unique_ptr is not sufficient.](#exclusive-ownership)
7. [Build Performance] Don't put unrelated utilities in a same file.
8. [Build Performance] Forward declare required types in headers.
9. [Build Performance] Move complex template definition in source whenever possible.
10. [Performance, Binary Size] Throw exceptions if you don't intend to handle/catch them.
11. [Build Performance] No non-one-liner function definition in header.
12. [Build Performance] No implementation detail in header. Follow pimpl idiom.
13. [Performance] Accept rvalue-ref function arguments when you mean it.
14. [UB] Never use 'const_cast' for writing on const-reference. It's UB.


### Avoid Memory Leaks

#### Never use raw pointers except in special cases.

We are using raw pointers almost everywhere in our codebase. However we are not adding more raw pointers. Slowly we are moving towards eliminating all the usage of raw pointers.

C++ guidelines ( C++14 onwards)  suggests that raw pointers are strongly discouraged from day to day application development work. The performance overhead of using unique_ptr over raw pointer is absolutely zero since unique_ptr has constexpr constructor. (Except the special case when we can avoid the check `ptr_ == nullptr` while deleting the pointer if ptr_ is always non-null because to our internal invariants)

1. We can use 'new' for creating raw pointer if it is being used immediately in a unique_ptr/shared_ptr for a type that has private constructor. For any other type we should use make_unique/make_shared instead.

2. We can use 'new'/'delete' for developing a C++ application/library, which is so much performance sensitive that we cannot afford to lose even a single cpu cycle. In that case the performance optimisation should demonstrate that it's benefit dominates the risk of the introducing bugs, developer overhead and program complexity.
In our codebase we are not developing a new operating system that we cannot simply use a make_unique over raw pointer. So it’s highly unlikely we will ever be in the situation of saving a couple of cpu cycles on the cost of bug vulnerability, developer overhead and program complexity.


### Runtime Performance

#### Throw exceptions but never catch them except in special cases

Throwing exceptions is encouraged but not catching. If you need to take decisions on exceptions, you should use error codes/error messages. C++ exception is not replacement of error handling. No path reachable from user input should throw exceptions. Exceptions should either crash the program or indicate the internal error (bugs). It’s allowed to catch exceptions at one place (at most)  - that is top level API handler, which can be used for sending internal-error/bugs alerts without crashing the system. It’s ok to catch exceptions in tests, only to validate the exception thrown in production code.

### Build Performance

#### Avoid 'Unrelated-Aggregation' Anti-Pattern

- Almost Never Use Static Member Functions For General Utilities in C++.
- Use global functions instead inside a utility namespace.
- Don't aggregate unrelated stuff in a file. Break them down into individual
  files.
- [Learn More Here](cpp/almost_never_use_static_member_fn_for_utils.md).


### Avoid Incorrect Binding

#### Don’t expose global level symbols in headers.

Don't declare `using A::B;` in global namespace in a header file. If we do so, the symbol `B` will be exposed in all the source file where this header is used. It not only pollutes the namespace of those source files but also leads to unexpected issues like - incorrect binding to different function. Sometimes that might get caught in compile time but in the worst case if signature of both function are same, compiler will bind the caller to wrong function. Which will lead to hard-to-discover issues.

To understand the scope of the problem, read this [stackoverflow answer](https://stackoverflow.com/a/1453605/2145334).


### Performance.Alloc

#### Don’t use unique_ptr as a substitute of std::optional.

unique_ptr allocates the object in heap. std::optional stores in memory. If std::unique_ptr is used only for the optional-ness of the object, we should be using std::optional (or boost::optional) instead to avoid unnecessary heap allocation.


### Exclusive Ownership

#### Don’t use shared_ptr unless unique_ptr is not sufficient.

Generally `shared_ptr` should be used with very much care. A shared_ptr object doesn't have explicit ownership of underlying object that might be lead to problems. For example thread-safety, object modification side effects etc. A unique_ptr guarantees exclusive ownership just like any other C++ object, hence it is much more safe.



## Appendix

References:

- [C++ Standard Working Draft](http://eel.is/c++draft/)


### Answers of quiz questions


**Ans1.** No. Not yet. If the value of reference `a` is read, it will be UB.

**Ans2.** No. Not for any possible input. The illegal instruction is not reachable.

**Ans3.** Yes. Signed Integer overflow is UB. This program will never terminate because compiler will replace this loop with infinite loop. Try it out with -O3 compiler option.

**Ans4.** No. Unsigned integer overflow on arithmetics is not UB. 

**Ans5.** Yes. Reading an uninitialized scaler is UB.

**Ans6.** Yes. Race condition have undefined behaviour (not just unspecified). hence the entire program will be illegal. Output can be anything.

**Ans7.** Either 'FG' or 'GF'.

**Ans8.** UB. scaler `k` was read before initialisation. Here two different things are involved. 1. Operator associativity of `operator>>` and 2. order of evaluation of the arguments of function `operator>>`.

Operator associativity says that `std::cin >> k >> a[k]` should be read as `((std::cin >> k) >> a[k])`, which is `operator>>(operator>>(std::cin, k), a[k])`. Let's assume alias `F = operator>>` for better readability.

So the expression is : `F(F(std::cin, k), a[k])`. Now comes order of evaluation for function arguments.

We could evaluate `F(std::cin, k)` first (that will initialize `k`) and then evaluate `a[k]`, that will create a entry in map `a`. and eventually `F(std::cin, a[k])` will set the value in a[k]. (assuming `F(std::cin, k)` returned `std::cin` )

or 

We could evaluate `a[k]` first, and then `F(std::cin, k)`. Evaluation of `a[k]` would result into UB, because scaler `k` is not initialized yet.

One of the two unspecified possibility have undefined behaviour. Hence the program have undefined behaviour.


**Ans9.** UB. Reading a memory that is not owned by a object you have access to, have undefined behaviour, no matter what is there on that memory. Note that practically it might have garbage value or zero, it doesn't matter. As per the standard the program has reachable UB hence it is illegal. Whether it works on your machine or not, is irrelevant.


**Ans10.** UB. Reading an uninitialized scaler has undefined behaviour. The memory allocation using 'new' only allocates memory for it and calls it's constructor. (constructor of scaler is nop). Constructor of a scaler does not initialize it. Hence the value at `*x` is uninitialised. `y` is trying to read it. Hence undefined behaviour. This UB is equivalent to UB in `int x; int y = x;`.

