# Wiki

The goal of this tool is to use the Wikipedia English dump to form graph
database that link relationship similar to ConceptNet. Like "earth" "haveAShape"
of "round". 

## Instruction for importing Wikipedia dump in XML to MySQL database
The first step is to import the English portion of Wikipedia into a mysql 
database so I query it as needed.

The first thought is to go to the [Wikipedia download page
](https://en.wikipedia.org/wiki/Wikipedia:Database_download).

So I have go to the XML files, and follow instructions provided by [this source
](https://stackoverflow.com/questions/40384864/importing-wikipedia-dump-to-mysql).

Basically, we need to use a tool called MWDumper, that will convert XML into 
SQL scripts. We can download the compile [java here
](https://github.com/bcollier/mwdumper/blob/master/build/mwdumper.jar), with 
the [instructions](https://www.mediawiki.org/wiki/Manual:MWDumper) here.

This code provided by the blog are mostly correct, except table page have one 
more column. All we need to do is to add the column like this:
```
ALTER TABLE page
ADD COLUMN page_counter INT AFTER page_restrictions;
```
Another change is that one of the column in revision is too small, so we need 
to change the field property.
```
ALTER TABLE `revision`
CHANGE `rev_comment` `rev_comment` blob NOT NULL AFTER `rev_text_id`;
```
There are also duplicate page_titles in page, so make sure they are not set to UNIQUE
```
ALTER TABLE `page`
ADD INDEX `page_name_title` (`page_namespace`, `page_title`),
ADD INDEX `name_title` (`page_namespace`, `page_title`),
DROP INDEX `page_name_title`,
DROP INDEX `name_title`;
```
After that it should just be a waiting game until everything is done. Happy NLPing!