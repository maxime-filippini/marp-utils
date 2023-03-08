# Marp utilities

Utilities for working with Marp presentations.

## How to use

Install the package using `pip`, either by cloning locally, or directly via this repository, i.e.

```console
pip install git+https://github.com/maxime-filippini/marp-utils
```

The package is called via the `marputils` command, which takes one of the following sub-commands as an input:

- `bootstrap`, which will help you bootstrap a new marp presentation.
- `process`, which will process an existing markdown file and export it to pdf. For more detail on this step of the process, please refer to the [dedicated sub-section](#processing-your-presentation-file) below.

### Bootstrapping a new presentation

The `bootstrap` command only has one parameter:
- `-f` or `--full`, which indicates whether to include all of the prompts for creating or file. If not supplied, the process is more streamlined, but relies on defaults set within `marputils`.


### Processing your presentation file

With the `process` command, the following items from your presentation can be acted upon:

- Any variable found in the body, which abides by the `${var_name}` syntax, will be replaced by the value supplied in the appropriate field in the frontmatter of the file. This process expects a `variable` dictionary in the frontmatter. An example of use case would be multiple references to the title of the presentation, for which the frontmatter and the first slide could look like this:

    ```markdown
    ---

    marp: true
    theme: my_theme
    variables:
        title: An awesome title
        subtitle: Isn't it great?
        date: 08/03/2023

    ---

    # ${title}
    ## ${subtitle}
    *${date}*
    ```

  Note: the frontmatter should be valid YAML.

- "Special comments", which expand to pre-defined content. For example, one can format section dividers by simply adding the following comment to a slide.

    ```
    <!-- section id="section_id" title="section title"-->
    ```

  This specific comment will expand into the following content:

    ```
    <!-- _header: <div id="section_id"></div> -->
    <!-- _class: divider -->
    # section title
    ```

    where the `_header` and `_class` comments have special meanings in `marp`, the latter indicating a specific class within our theme, and the former the contents of the header for the slide. Here, our header only contains an empty `<div>`, which we can use for referencing.

- Python code blocks can be evaluated and their output displayed. Let us consider the piece of markdown below. We add some information on our code block header, namely an `id` and a flag to tell the code block needs to be run (i.e. `run="true"`).

  The comments wrapped by `# <` and `> #` are setup lines, which need to be executed before the rest of the code. Here, we define a variable and assign it a value.

  Finally, we tell `marputils` where the output needs to be included, via the `<!-- code -->` comment, which refers to our block's id.

    ````
    ---

    # Example of a code block

    ```python id="A" run="true"
    # <
    # a = 32 ** 3
    # >
    print(a)
    ```

    <!-- code id="a" -->

    ---
    ````
  The resulting slide, after processing, would be:

  ````
  ---

  # Example of a code block

  ```python id="A" run="true"
  print(a)
  ```

  ```python
  32768
  ```

  ---
  ````

The parameters of the `process` command are the following:

- `-p` or `--path`, which is the path to your marp presentation.
- `-o` or `--out_path`, which is the path to the resulting file. If not supplied, a file named `build.md` will be created in the directory of the source file.
- `-w` or `--watch`, which is a flag indicating whether the file supplied in `--path` is to be watched for modifications. If supplied, the processing pipeline will run on each save of the source file.
- `-e` or `--export`, which is a flag indicating whether to export the presentation to `.pdf` after processing. NOTE: This requires the `marp-cli` to be installed, for which instructions can be found [here](https://github.com/marp-team/marp-cli#install).

Here is an example of a command:

```console
marputils process -p ./data/demo.md -e ./data/demo.pdf --watch
```



## To do

Here are some elements which are being/will be worked on to make `marputils` better.

- [ ] Automated table of contents based on dividers/headings
- [ ] Make it so only lines which have a comment or a variable need to be parsed.
- [ ] Enable way to register the tags so the processor can directly know the subclasses available
