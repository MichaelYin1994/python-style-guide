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

#### 2.1.4 结论
确保对代码应用`pylint`。

抑制不准确的警告，以便能够将其他警告暴露出来。你可以通过设置一个行级别的注释来抑制警告。例如:
```Python
dict = 'something awful'  # Bad Idea... pylint: disable=redefined-builtin
```
`pylint`警告是以符号名(如`empty-docstring`)来标识的。google特定的警告则是以`g-`开头。如果警告的符号名不够见名知意，那么请对其增加一个详细解释。采用这种抑制方式的好处是我们可以轻松查找抑制并回顾它们。

你可以使用命令`pylint --list-msgs`来获取pylint告警列表。你可以使用命令 `pylint --help-msg=C6409`，以获取关于特定消息的更多信息。

相比较于之前使用的`pylint: disable-msg`，本文推荐使用`pylint: disable`。

在函数体中`del`未使用的变量可以消除参数未使用告警。总是记得要加一条注释说明你为何`del`它们，注释使用"Unused"就可以，例如：
```Python
def viking_cafe_order(spam, beans, eggs=None):
    del beans, eggs  # Unused by vikings.
    return spam + spam + spa
```
其他消除这个告警的方法还有使用`_`标识未使用参数，或者给这些参数名加上前缀 `unused_`，或者直接把它们赋值给`_`。这些方法都是允许的，但是已经不再被鼓励使用。前两种方式会影响到通过参数名传参的调用方式，而最后一种并不能保证参数确实未被使用。

### 2.2 Imports
--------------------
只在import包和模块的时候使用`import`，而不要用来import单独的类或函数。(这一条对于[typing_module](https://google.github.io/styleguide/pyguide.html#typing-imports)模块的imports例外)

#### 2.2.1 定义：
一个模块到另一个模块之间共享代码的复用性机制。

#### 2.2.2 Pros：
命名空间管理约定简单，每个标识符的源都以一种一致的方式指明。例如`x.Obj`表示`Obj`是在模块`x`中定义的。

#### 2.2.3 Cons：
一方面，模块名可能会有冲突；另一方面，一些模块名可能很长，不太方便。

#### 2.2.4 结论：
* `import x`（当`x`是包或模块）
* `from x import y`（当`x`是包前缀，`y`是不带前缀的模块名）
* `from x import  y as z`（如果两个要导入的模块都叫做`y`或者`y`太长了不利于引用的时候）
* `import y as z`（仅在当`z`是通用的缩写的时候使用，例如`import numpy as np`）

例如，模块`sound.effects.echo`可以用如下方式导入：
```Python
from sound.effects import echo
...
echo.EchoFilter(input, output, delay=0.7, atten=4)
```
导入时不要使用相对名称。即使模块在同一个包中，也要使用完整包名。这能帮助你避免无意间导入一个包两次。

从[typing module](https://google.github.io/styleguide/pyguide.html#typing-imports)和[six.moves module](https://six.readthedocs.io/#module-six.moves)进行import不适用上述规则。

### 2.3 包
--------------------
使用模块的全路径名来import包(Package)中的每个模块。

#### 2.3.1 Pros
能够避免模块名冲突以及由于模块搜索路径与作者预期不符而造成的错误引用。让查找模块更简单。

#### 2.3.2 Cons
让部署代码时有些困难，因为你必须复制包层次结构。不过对于现在的部署机制而言，这其实不是问题。

#### 2.3.3 建议
所有的新代码都应该用完整包名来import每个模块。

import示例应该像这样：

**Yes:**
```Python
# Reference absl.flags in code with the complete name (verbose).
# 在代码中使用完整路径调用absl.flags
import absl.flags
from doctor.who import jodie

FLAGS = absl.flags.FLAGS
```
``` Python
# Reference flags in code with just the module name (common).
# 在代码中只用模块名来调用flags
from absl import flags
from doctor.who import jodie

FLAGS = flags.FLAGS
```

**No:**（假设文件在`doctor/who`中，并且`jodie.py`也在该路径下）
```Python
# Unclear what module the author wanted and what will be imported. The actual
# import behavior depends on external factors controlling sys.path.
# Which possible jodie module did the author intend to import?
# 不清楚作者想要哪个模块以及最终import的是哪个模块,
# 实际的import操作依赖于受到外部参数控制的sys.path
# 那么哪一个可能的jodie模块是作者希望import的呢?
import jodie
```
不应假定主入口脚本所在的目录就在`sys.path`中，虽然这种情况在一些环境下是存在的。当主入口脚本所在目录不在`sys.path`中时，代码将假设`import jodie`是导入的一个第三方库或者是一个名为`jodie`的顶层包，而不是本地的`jodie.py`。

### 2.4 异常
--------------------
异常处理是允许被使用的，但使用时务必谨慎。

#### 2.4.1 定义
异常是一种从正常代码段控制流中跳出以处理错误或者其他异常条件的手段。

#### 2.4.2 Pros
正常代码的控制流时不会被错误处理代码影响的。异常处理同样允许在某些情况下，控制流跳过多段代码，例如在某一步从N个嵌入函数返回结果而非强行延续错误代码。
