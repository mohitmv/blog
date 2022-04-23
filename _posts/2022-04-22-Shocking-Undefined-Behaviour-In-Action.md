---
layout: post
title: "Shocking Examples of Undefined Behaviour In Action"

---

As we know that Undefined Behaviour (UB) is a dangerous thing in C++. Still it remains difficult to explain to those who have not seen it's horror practically.

Those individual claims UB is bad in theory, but not so bad practically as long as thing works in practice because compiler developers are not evil.

This blog presents a few "shocking" examples to demonstrate UB in action.

### Example1 : A simple finite loop turning into infinite loop

{% highlight c++ %}

int main() {
  char buf[50] = "y";
  for (int j = 0; j < 9; ++j) {
    std::cout << (j * 0x20000001) << std::endl;
    if (buf[0] == 'x') break;
  }
}

{% endhighlight %}

[https://godbolt.org/z/Y6bTP3MK3](https://godbolt.org/z/Y6bTP3MK3) (Originally shared by Eric Musser)

We can see that this simple finite loop is turned into infinite loop in `-O3` optimization mode with `gcc-11.2 x86-64` but it works fine in `-O0` mode.

This program has UB (signed integer overflow). There are two optimisations involved.

First one translates it to:

{% highlight c++ %}

for (int p = 0; p < 9 * 0x20000001; p += 0x20000001) {
  std::cout << p << std::endl;
  if (buf[0] == 'x') break;
}

{% endhighlight %}

This optimisation is legal because compiler can safely assume that range of `int` is actually `-infinite` to `+infinite`. The range `{INT_MIN, INT_MAX}` is for C++ developers, not for compilers.

Second optimisation reduces 'j < 9 * 0x20000001' to true because RHS is more than INT_MAX. and j being an integer cannot be more than INT_MAX. This for-loop now becomes

`for (int j = 0; true; j+=...) {....}`

and hence infinite loop.

### Example2 : EraseAll function being called

{% highlight c++ %}

typedef int (*Function)();

static Function Do;

static int EraseAll() {
  std::cout << "Disaster Ahead" << std::endl;
  // system("rm -rf /");
  return 0;
}

void NeverCalled() {
  Do = EraseAll;  
}

int main() {
  return Do();
}

{% endhighlight %}

[https://godbolt.org/z/3Pqojanqo](https://godbolt.org/z/3Pqojanqo) (Originally shared by [Krister Walfridsson](https://kristerw.blogspot.com/2017/09/follow-up-on-why-undefined-behavior-may.html))

In this example, `EraseAll` is never called, but when we run this program with `Clang-10.0.0 x86-64`, it prints `"Disaster Ahead"`. Which also means it will run `system("rm -rf /")` if we uncomment it.

This program has UB (nullptr dereferencing).

In this program, compiler can see that variable `Do` is static, hence it cannot be read/written by other function in different translation units. Since the scope of `Do` is limited to this TU, compiler can deduce at compile time that possible values of `Do` cannot be anything other than `{nullptr, EraseAll}`.

Further compiler can guarantee that it cannot have `nullptr` value, because the program will have UB in that case. Hence it can safely assume that possible values of `Do` are only `{EraseAll}`. Since there is only possible value of `Do` during it's lifetime in a legal program, it's good optimization to initialize `Do` by `EraseAll` and never set it again, i.e. replace `NeverCalled` by a nop function - `void NeverCalled() { }`

Hence `int main() { return Do(); }` is replaced by `int main() { return EraseAll(); }`

Which leads to disaster - `system("rm -rf /")`.


More about [Undefined Behaviour here](https://mohitmv.github.io/blog/Cpp-Undefined-Behaviour-101/).

