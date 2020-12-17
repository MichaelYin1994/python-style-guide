背景
================================

Python 是 Google主要的脚本语言。这本风格指南主要包含的是针对python的编程准则。

为帮助读者能够将代码准确格式化，我们提供了针对[Vim的配置文件](https://google.github.io/styleguide/google_python_style.vim)。对于Emacs用户，保持默认设置即可。许多团队使用[yapf](https://github.com/google/yapf/)作为自动格式化工具以避免格式不一致。

Python语言规范
================================

### 2.1 Lint
--------------------
使用该 [pylintrc](https://google.github.io/styleguide/pylintrc)对你的代码运行`pylint`

#### 2.1.1 定义:
`pylint`是一个在Python源代码中查找bug的工具。对于C和C++这样的不那么动态的(译者注: 原文是less dynamic)语言，这些bug通常由编译器来捕获。由于Python的动态特性，有些警告可能不对。不过伪告警应该相对较少。

#### 2.1.2 优点:
可以捕获容易忽视的错误，例如输入错误，使用未赋值的变量等。

#### 2.1.3 缺点:
`pylint`不完美。要利用其优势，我们有时侯需要：a) 围绕着它来写代码 b) 抑制其告警 c) 改进它 或者d) 忽略它。

#### 2.1.4 Decision
确保对代码应用`pylint`。

抑制不准确的警告，以便能够将其他警告暴露出来。你可以通过设置一个行级别的注释来抑制警告。例如:
```Python
dict = 'something awful'  # Bad Idea... pylint: disable=redefined-builtin
```