---
layout: post
title: "How can they say ++it is faster than it++"

---

This is **NOT true** for the iterators of **100%** of the **STL containers** - including the commonly used ones - `std::vector`,    `std::unordered_map`,    `std::array`,   `std::list`,   `std::unordered_set`,   `std::map`,   `std::set`,   `std::queue` and **ALL** others.

This is obviously **NOT true** for primitive types. No explanation required.

This is **NOT true** for the iterators of **99.99999999%** of the **non-STL templated containers (custom implemented)** ever written in the entire C++ world except those which were written for extremely specialized use case in which they couldn't ensure [`TriviallyCopyable`](https://en.cppreference.com/w/cpp/named_req/TriviallyCopyable) requirnment for iterator... but hey, for those super specialized 0.00000001% use case, they are not likely to support `it++` anyway, so nothing to worry.


## Why this discussion on the first place

Because of misleading information:

![Misleading Posts]({{site.baseurl}}/images/pre_increment/misleading_post_stamped_resize1.png "Misleading Posts")

## Why `++it` performs identically to `it++`

because cost of copying a [`TriviallyCopyable`](https://en.cppreference.com/w/cpp/named_req/TriviallyCopyable) object is ZERO if it's unused later.

It's NOT almost-zero. It's absolute ZERO.

Note:

1). Compilers can figure out if it's unused or not. It works in `O1`, `O2` and `O3` mode.

2). `operator++` for templated iterator is inlined.

In this code:

{% highlight c++ %}
struct R {
  ...;
};

struct S {
  R* x;
  int y;
};

S Func1(S& s) {
  S s1_copy = s;
  s.x++;
  s.y++;
  return s1_copy;
}

S& Func2(S& s) {
  s.x++;
  s.y++;
  return s;
}

Func1(s);
Func2(s);
{% endhighlight %}


`Func2(s)` is NOT faster than `Func1(s)`.

## Let's look at the machine code:

Let's take an example of `std::list`:

{% highlight c++ %}
int F3(const std::list<int>& v) {
    int output = 0;
    for (auto it = v.begin(); it != v.end(); it++) {
        output += *it;
    }
    return output;
}

int G3(const std::list<int>& v) {
    int output = 0;
    for (auto it = v.begin(); it != v.end(); ++it) {
        output += *it;
    }
    return output;
}
{% endhighlight %}


`F3` and `G3` differs only on `it++` and `++it`.

Here is the diff of their assembly code. There is absolutely no diff at all except their names `F3` and `G3`.

![Assembly diff]({{site.baseurl}}/images/pre_increment/std_list_pre_increment_diff.png "Assembly diff")

See the assembly code and diff yourself:

1). Post Increment [https://godbolt.org/z/vEh5hPv3r](https://godbolt.org/z/vEh5hPv3r)

2). Pre Increment [https://godbolt.org/z/nnqWjno7P](https://godbolt.org/z/nnqWjno7P)

3). The diff in assembly code: [https://www.diffchecker.com/YXPlSDRZ](https://www.diffchecker.com/YXPlSDRZ)

## A bit more complex case

Note: Passing non-TriviallyCopyable type to templated container won't make it's iterator non-TriviallyCopyable.

See example below for `std::list<S>`, `std::set<S>`, `std::unordered_set<S>`,

where `S = std::vector<int>;`  (Non trivially copiable type)


1). Post Increment [https://godbolt.org/z/EGWoTqove](https://godbolt.org/z/EGWoTqove)

2). Pre Increment [https://godbolt.org/z/jKhYPGWf7](https://godbolt.org/z/jKhYPGWf7)

3). The diff in assembly code: [https://www.diffchecker.com/yaSmJLV2](https://www.diffchecker.com/yaSmJLV2)

In this case also assembly code is same for `it++` and `++it`.



## Should we prefer `it++` over `++it` ?

This article does NOT advocate usage of `it++` over `++it`.

I personally use `++it` all the time.

This article only challenges the statement that `++it` is faster than `it++`.

<!--

## Discussion:

<iframe id="reddit-embed" src="https://www.redditmedia.com/r/cpp/comments/v2u0ld/how_dare_they_say_it_is_faster_than_it/?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" height="127" width="640" scrolling="no"></iframe>

-->
