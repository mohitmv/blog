---
layout: post
title: "How dare they said ++it is faster than it++ for iterators"

---

This is **NOT true** for **100%** of the **STL containers** - including the commonly used ones - `std::vector`, `std::unordered_map`, `std::array`, `std::list`, `std::unordered_set`, `std::map`, `std::set`, `std::queue` and **ALL** others.

This is obviously **NOT true** for primitive types. No explaination required.

This is **NOT true** for **99.99999999%** of the **non-STL templated containers (custom implemented)** ever written in the entire C++ world except those which were written for extremely specialized use case in which they couldn't ensure `TriviallyCopyable` requirnment for iterator... but hey, for those super specialized 0.00000001% use case, they are not likely to support `it++` anyway, so nothing to worry.


## Why this discussion on the first place

Because of misleading information:

![Misleading Posts]({{site.baseurl}}/images/pre_increment/misleading_post_stamped_resize1.png "Misleading Posts")

## Why `++it` performs identically to `it++`

because cost of copying a [`TriviallyCopyable`](https://en.cppreference.com/w/cpp/named_req/TriviallyCopyable) object is ZERO if it's unused later.

It's NOT almost-zero. It's absolute ZERO.

Note:

1). Compiler can figure out if it's unused or not.

2). `operator++` for templated iterator is inlined.

In this code:

```
struct R {
  ...;
};

struct S {
  R* x;
  int y;
};

S F1(S& s) {
  S s1_copy = s;
  s.x++;
  s.y++;
  return s1_copy;
}

S& F2(S& s) {
  s.x++;
  s.y++;
  return s;
}

F1(s);
F2(s);

```

`F2(s)` is NOT faster than `F1(s)`.

## Let's look at the machine code:

1). Post Increment https://godbolt.org/z/vEh5hPv3r

2). Pre Increment https://godbolt.org/z/nnqWjno7P

```
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
```

Here is the diff in their assembly code. Absolutely No diff at all except their names "F3" and "G3".

![Assembly diff]({{site.baseurl}}/images/pre_increment/std_list_pre_increment_diff.png "Assembly diff")

See the diff yourself: [https://www.diffchecker.com/YXPlSDRZ](https://www.diffchecker.com/YXPlSDRZ)

