---
layout: post
title: "CTwik : General Purpose Hot Patcher For C++"

---

Hi, This is Mohit Saini. I built CTwik for general purpose hot patching in a
C++ process.

CTwik enables developers to hot patch their C++ code change, to a running C++ application, without even restarting the application.

CTwik-client comes with a directory watcher, which automatically keeps on figuring out the code change anywhere in repo, compute diff, and figure out the minimal set of functions which needs to be recompiled for patching.

CTwik-server, which must be running in a dedicated thread in the main C++ Application, receive the patch request from CTwik-client and dynamically inject the patch at runtime, by changing the machine code of current-process (itself) to reflect the behaviour change of App, as per the changed code.

CTwik can take care of almost any kind of code change, including the change in header files, function signatures, struct/class layouts, global variables, class layout of global variables, local static etc.

CTwik typically takes a few seconds for end to end patching, after the code change is saved in text-editor.

<iframe style='border:none; width:500px; height: 300px;' src="http://www.youtube.com/embed/e7wm8pw2Yw0" >&nbsp;</iframe>




### Why do we need hot patching ?

- As we know that, a typical development cycle involves code change locally, recompiling/rebuilding the entire App, publishing the executable to target machine, restarting the App, waiting for the App to be in ready state, etc.
- App restart will loose in-memory state.
- App restart brings App downtime.
- App restart can a lot of time, sometime minutes, which becomes bottleneck in developer's productivity.
- Rebuilding the entire App can take minutes, when dealing with big projects, which have executables of size 200MBs.
- With hot-patching, we can skip all these steps within a few seconds


### Where else CTwik can be used ?

- Hot patching bug fixes to long running Apps in production.
- Hot patching security fix to long running operating systems or Patching the new version of OS on top of previous one.
- Live debugging on a customer cluster without restarting services. Check the values of some internal C++ variables by patching a function which prints some info.
- And many other use case can be served with hot patching.



### State of the art in hot patching

- Hot patching is trivial for Python. There are many tools for hot patching. Also, one can write their own hot patcher in 100 lines because of REPL (exec and eval) in Python.
- Hot patching is a bit hard for Java. Still there are couple of open source tools, which enables to hot swap a a Java class, because of JVM layer.
- Next to Impossible in C++. There are no general purpose hot patcher for C++ which work reliably, for Application in production environment, without requiring developer having to know about their internal detail and requiring a lot of custom handling in code.


Hot Patching is hard in C++, because once the App starts, there is only machine code, which runs directly on the hardware. There is no software abstraction to control it, unless we change the machine code itself of currently running process.

### Why CTwik

- CTwik is the first tool in the industry, to implement general purpose hot patching, which covers 99% of the typical code changes. The major change it doesn't cover, are the change in the 'main' function and other top level functions which are above user's API handlers. Those top level boilerplates are rarely changed over time.


### CTwik Implementation Summary

- There are two parts of CTwik - Client and Server.
- Client deals with C++ code diff and extracting out the minimal set of functions which needs to be recompiled and create a shared library of changed functions.
- Client also read the shared library using ELF reader, to extract the function symbols and their corresponding function pointers (Memory address in machine code section where the function definition starts).
- Client sends the binary content of shared library and other metadata over TCP request.
- CTwik-Server dump the received binary content of shared library in a file, and open it using "dlopen", figures out the new definition (new function pointers) of the patched symbols.
- CTwik-Server change the machine code of current process, to redirect the old function definitions, to the new definitions (new function pointer). This is supported only for x86-64 machines. To redirect, we overwrite the first 12 bytes in the old function definitions, to new instruction "long jump to new fn ptr" 
(moveabs %rax 0xVV ; jmp %rax). Here '0xVV' is the 64 bit new value of function ptr.
- [Beta Implementation] For global data symbols, we change their entry in global offset table, so that old functions (including the unpatched), will be referring to their new value from shared library. To support this, entire application code needs to be compiled with '-fPIC' option.


### CTwik-Client Implementation Details

Let's understand the 'extracting minimal set of function' piece with an example. Consider a translation unit (TU) 'file1.cpp' containing following code.

```C++
// file1.cpp

#include <stdio.h>

void G( ) {
  ...
}

int F(int x) {
  x += 50;
  printf("x = %d\n", x);
  return x;
}

void P( ) {
  ... 
}

int F2(int x) {
  return F(x) + 2;
}

// 100 more functions.
...
```

- In this translation unit, if some code is changed in function F (let's say 50 is replaced by 51), we have to recompile F and F2.  The reason why F2 needs to be recompiled, is, F2 can access the implementation of F, and hence F's definition could be inlined in F2, and the machine code of F2 might not be calling F.

- To compile F and F2, we need 'printf' declaration as well. Hence, the minimal set of code that needs to be recompiled, would be 'minimal_change.cpp'.

```C++
// minimal_change.cpp

extern "C" int printf(const char *format, ...);

int F(int x) {
  x += 51;  // Changed value.
  printf("x = %d\n", x);
  return x;
}

int F2(int x) {
  return F(x) + 2;
}
```

- In this particular example, it can be observed that recompiling the file1.cpp after changing  50 to 51, will produce the exact same machine code, except for the function 'F' and 'F2'. Hence 'F' and 'F2' are the minimal and sufficient set of functions which needs to be recompiled, and hot patching the new definition of 'F' and 'F2' will make the live C++ process behave equivalent to how it would behave if we could have rebuild the main executable again and restart the process.


### How to figure out minimal set of functions automatically ?


CTwik parse a translation unit (after preprocessing) into graph of global entities. A global C++ entity is a global definition or declaration. An entity could be anything like struct, class, function declaration, function definition, typedef, global variable declaration/definition etc. Each entity declaration / definition introduce a name for it, which can be referred in other entities. For example -  struct S { ...  };    is an entity with name "S".  `int F2(int x) { return F(x) + 2; }` is an entity with name "F2".  Globally defined `int x = 5;` is another entity.

#### Note that:

- we are not considering the entities inside function-scope. The entire body of a function definition is considered as single entity.
- Each entity has a name. There could be multiple entities with same name (example function overloading etc.)
- Entity name is the fully qualified name of an entity w.r.t. namespace.


{% highlight ruby %}
def print_hi(name)
  puts "Hi, #{name}"
end
print_hi('Tom')
#=> prints 'Hi, Tom' to STDOUT.
{% endhighlight %}


ToDo: Add more content here from https://mohit-saini-blog.blogspot.com/2021/09/ctwik-general-purpose-hot-patcher-for-cpp.html

