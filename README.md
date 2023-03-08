# Marp utilities

Some utilities for working with Marp presentation. Currently includes a command line tool for:
- Bootstrapping a new presentation
- Processing a presentation file to replace special comments and flags with variables


## To do

- [ ] Rename divider tags as section tags
- [ ] Automated table of contents based on dividers
- [ ] Introduce second header to jump to the beginning of the section
- [ ] Make it so only lines which have a comment or a variable need to be parsed.
- [ ] Enable way to register the tags so the processor can directly know the subclasses available
- [ ] Implement other types of "special slides" (sub-dividers, special format for first or last slide)
- [ ] Implement a way to watch a file and process it live on change
