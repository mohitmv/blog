---
layout: post
title: "Undefined Behaviour in C++"

---

The introduction of C++ starts with the most important thing about C++, the Undefined Behaviour (UB). UB exists only in C/C++, or their sibling languages (eg: Rust, Circle etc.), having similar performance goals. UB doesn't exists in most of the programming languages like Java, Python, Perl, Groovy, JavaScript, TypeScript, Bash, Go.

If you are coming from these language to C++, it's very important to understand the UB very well.

For any programming language, there exists a definition of valid program. Given any string made of ascii characters, the string is either defined to be a valid program of that language or not.

Most of the programming languages requires that execution of every valid program should give correct result, and execution/compilation of every illegal program should fail.
Note: here correct result is defined w.r.t intent of the program.
For example, the Java program:

{% highlight c++ %}
public static void main(String[] args) {
  1/0;
}
{% endhighlight %}

raise exception. and that was the intent. Hence the result (exception) is correct.

and the following Java program is illegal. Hence compilation fails.

{% highlight c++ %}
public public static void main() { }
{% endhighlight %}

However C/C++ doesn't require that execution/compilation of every illegal program should fail. A program can be illegal and still it can work. Repeating it once more - **"A C++ program can be illegal and still work as you wished"**. That's what the danger is all about.

- An illegal C++ program might stop working tomorrow.
- It might stop working on Friday and Monday but works rest of the week.
- It might work all the time except when you have to demonstrate your App to customers.
- It might stop working if you run it after eating large pizza but works if you run it after eating sandwich.

And, it's **perfectly legal** for a C/C++ compiler to do this with a program. A Java compiler don't have liberty to do this.


C/C++ standard require that execution of every valid program should give correct result, but if the program is illegal then the behaviour is either defined to be diagnosable by compiler or the behaviour is undefined.

If the illegal program is defined to be diagnosable by compiler, any standard compliant compiler is obliged to fail the compilation (Possibly with readable errors). However if a illegal program doesn't fall into definition of diagnosable program, compiler have full liberty to do anything with that program.

For a program with reachable UB, it's legal for a compiler to generate an executable:

- That gives incorrect output.
- That is an empty executable.
- Whose execution deletes all the data from your hard drive.
- Whose execution explode and burn the computer.
- Whose execution invoke the API to crash the engine of rocket in which this program is running.

All that is legal for a standard compliant compiler to do.

Humorously, Undefined behaviour is also called "nasal demons". Here is the context:

> The term originally originated from a post by John F. Woods on 2/25/1992 in a discussion on the Usenet group comp.std.c[1]. Mr Woods was attempting to emphasis the fact that undefined behaviour may legally (as far as the standard is concerned) result in the compiler doing just about anything - including but not limited to "having demons fly out of your nose". The aim of the post was to make the point that one cannot put the compiler at fault for input which has no defined behaviour as far as the c standard is concerned.

> References:
- [https://accu.org/journals/overload/21/115/maudel_1857/](https://accu.org/journals/overload/21/115/maudel_1857/)
- [https://en.wikichip.org/wiki/nasal_demons](https://en.wikichip.org/wiki/nasal_demons)
- [https://en.wikipedia.org/wiki/Undefined_behavior](https://en.wikipedia.org/wiki/Undefined_behavior)


So far we have seen the danger of UB. Now the next question is, why did C++ standard give such powerful liberty to compilers ?

The answer is, "Optimizations". C++ Compilers assumes a lot of things due to UB. These assumptions enables optimizations.

Consider the example:

{% highlight c++ %}
int* a = new int[10];
a[20] = 4;
{% endhighlight %}

This program is writing at illegal memory (UB). Consequence of this program cannot be even measured. This one illegal write can cause this program to delete entire disc. Imagine there were filepath chars written at `a[20]` address, to be used by some other function in this program. This `a[20] = 4` changes that filepath to something, matching with filepath of entire disc. So the other function that was supposed to delete only one file, will end up deleting entire disc.

How java handles it:

Java translate this code into something like:

{% highlight c++ %}
if (20 < a.length) {
  a[20] = 4
} else {
  throw new Exception("Out of Index");
}
{% endhighlight %}

Which is safe but require an extra `if` check. `C++` cannot afford an extra `if` for every memory read-write. So C++ simply declare illegal memory access a `UB`, so that compiler don't have to check validity of memory and still remain standard compliant.


Note that `C++` is not a programming language that can be learnt by trial and errors. A lot of things are wrong but works. Only way to know if a program is legal or not, is to get it stamped by C++ standard.


C++ standard says, if an instruction with undefined behaviour is reachable in C++ program, the behaviour of entire program is undefined, including the instruction preceding the first occurrence of undefined behaviour.

This statement from C++ standard allows compiler to eliminate the code blocks that has reachable path to UB.

Short quiz : what would be the output of this program on sufficiently optimised compiler, for argc = 1 and 2 respectively ?

{% highlight c++ %}
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
{% endhighlight %}


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
`a + b > a`. This assumptions allows a lot of compiler optimisations.

(Side Note: overflow by arithmetic ops on unsigned integers have well defined semantics)


Consider this program (by @eric.musser )

{% highlight c++ %}
int main() {
    char buf[50] = "y";
    for (int j = 0; j < 9; ++j) {
        std::cout << (j * 0x20000001) << std::endl;
        if (buf[0] == 'x') break;
    }
}

{% endhighlight %}

https://godbolt.org/z/bzrbox

It goes in infinite loop.

Why ?

Because it involves undefined behaviour (signed integer overflow). There are two optimisations involved.

First one translates it to:

{% highlight c++ %}
  for (int p = 0; p < 9 * 0x20000001; p += 0x20000001) {
      std::cout << p << std::endl;
      if (buf[0] == 'x') break;
  }
{% endhighlight %}

Second optimisation reduces `'j < 9 * 0x20000001'` to `true` because RHS is more than INT_MAX. and `j` being an integer cannot be more than INT_MAX.
So that for loop now becomes

for (int j = 0; true; j+=...) {....}


and hence infinite loop.

Moral of the story : Stay away from the 'undefined behaviour'.


Short Quiz

Q1. Does this program have UB ? Explain.

{% highlight c++ %}
int x[10];
int* a = x + 20;
{% endhighlight %}

Q2. Does this program have UB ? Explain.

{% highlight c++ %}
int main(int argc, char* argv[]) {
  if (argc > argc) {
    int x[10];
    int a = x[20];
  }
}
{% endhighlight %}

Q3. Does this program have UB ? Explain.

{% highlight c++ %}
for (int i = 2; i > 1; i++) {
  std::cout << i << std::endl;
}
{% endhighlight %}

Q4. Does this program have UB ? Explain.

{% highlight c++ %}
for (uint i = 2; i > 1; i++) {
  std::cout << i << std::endl;
}
{% endhighlight %}

Q5. Does this program have UB ? Explain. What would be output of this program ?

{% highlight c++ %}
int x;
x = x * 0;
std::cout << x << std::endl;
{% endhighlight %}

Q6. Does this program have UB ? Explain. Will assertion fail or no ?

{% highlight c++ %}
int a = 4;

void Thread1() {
  a++;
}

void Thread2() {
  int b = a;
  assert(b == 4 || b == 5);
}

{% endhighlight %}

#### Unspecified Behaviour

Unspecified behaviour is different from undefined behaviour. Presence of reachable **'undefined behaviour'** makes the entire program illegal. However **'unspecified behaviour'** is not that serious. If value/state of an object is unspecified, it means the object is valid and it's value is one of the valid value from it's value-space, however there is no guarantee which one value.
For example:

{% highlight c++ %}
vector<int> v = {10, 20, 30};
auto v2 = std::move(v);
// At this point value of v is unspecified. However it's value is exactly one
// of the possible value of vector<int>.
{% endhighlight %}

#### Unspecified Evaluation Order

Q7. What should be output of this program ?

{% highlight c++ %}
int F() { std::cout << 'F'; return 10; }
int G() { std::cout << 'G'; return 20; }
int H() { std::cout << 'H'; return 20; }
int main() {
  int x = F() + G() + H();
}
{% endhighlight %}

As per C++ standard order of evaluation of a function-call argument is unspecified. (Special rule for scalers args).

Hence the output of the program above could be `FGH` or `HGF` or `FHG` or `GFH` or `GHF` or `HFG`. However there doesn't exists any other possibility of the output of this program.

Short Quiz

Q8. What would be output of this program, for stdin input '15 5 '.

{% highlight c++ %}
int k;
std::unordered_map<int, int> a;
std::cin >> k >> a[k];
std::cout << a[k];
{% endhighlight %}

Q9. What would be output of program below ?

- Option A). Garbage (Unspecified Value)
- Option B). 0
- Option C). UB.
- Option D). 0 if it is single threaded program else it could be garbage.

{% highlight c++ %}
int* x = new int();
delete x;
int y = *x;
std::cout << y;
{% endhighlight %}


Q10. What would be output of this program ?

- Option A). Garbage (Unspecified Value)
- Option B). 0
- Option C). UB.
- Option D). 0 if it is single threaded program else it could be garbage.

{% highlight c++ %}
int* x = new int();
int y = *x;
delete x;
std::cout << y;
{% endhighlight %}


## Appendix

References:

- [C++ Standard Working Draft](http://eel.is/c++draft/)


### Answers of quiz questions


**Ans1.** No. Not yet. If the `a` is dereferenced, it will be UB.

**Ans2.** No. Not for any possible input. The illegal instruction is not reachable.

**Ans3.** Yes. Signed Integer overflow is UB. This program will never terminate because compiler will replace this loop with infinite loop. Try it out with -O3 compiler option.

**Ans4.** No. Unsigned integer overflow on arithmetics is not UB. 

**Ans5.** Yes. Reading an uninitialized scaler is UB.

**Ans6.** Yes. Race condition have undefined behaviour (not just unspecified). hence the entire program will be illegal. Output can be anything.

**Ans7.** `FGH` or `HGF` or `FHG` or `GFH` or `GHF` or `HFG`.

**Ans8.** UB. scaler `k` was read before initialisation. Here two different things are involved. 1. Operator associativity of `operator>>` and 2. order of evaluation of the arguments of function `operator>>`.

Operator associativity says that `std::cin >> k >> a[k]` should be read as `((std::cin >> k) >> a[k])`, which is `operator>>(operator>>(std::cin, k), a[k])`. Let's assume alias `F = operator>>` for better readability.

So the expression is : `F(F(std::cin, k), a[k])`. Now comes order of evaluation for function arguments.

We could evaluate `F(std::cin, k)` first (that will initialize `k`) and then evaluate `a[k]`, that will create a entry in map `a`. and eventually `F(std::cin, a[k])` will set the value in a[k]. (assuming `F(std::cin, k)` returned `std::cin` )

or 

We could evaluate `a[k]` first, and then `F(std::cin, k)`. Evaluation of `a[k]` would result into UB, because scaler `k` is not initialized yet.

One of the two unspecified possibility have undefined behaviour. Hence the program have undefined behaviour.


**Ans9.** UB. Reading a memory that is not owned by a object you have access to, have undefined behaviour, no matter what is there on that memory. Note that practically it might have garbage value or zero, it doesn't matter. As per the standard the program has reachable UB hence it is illegal. Whether it works on your machine or not, is irrelevant.


**Ans10.** output = 0.

  Reading an uninitialized scaler has undefined behaviour, but here the scaler is default-constructed. The memory allocation using 'new' allocates memory and calls it's default-constructor.
  Note that there a different rules for constructor of scalers.

  - `int x; int y = x;` This is UB, because `x` is constructed but not initialized. i.e. the lifttime of variable x have started but it's not initialized to a value.

  - `auto x = int(); int y = x;` This is valid program, and the value of y will be 0. Here `x` is default-constructed and initialized with value 0.

  - `int* x = new int(); int y = *x;` For the same reason above, this is a valid program.

