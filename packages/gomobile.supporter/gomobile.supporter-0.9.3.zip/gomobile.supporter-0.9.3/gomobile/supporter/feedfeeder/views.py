from Products.feedfeeder.browser import feed as base

class FeedFolderView(base.FeedFolderView):

    def get_batched_items(self):
        """Return all feed items.

        Currently implemented as a generator since there could
        theoretically be tens of thousands of items.
        """

        print "Getting results"

        listing = self.context.getFolderContents

        results = listing({'sort_on': 'getFeedItemUpdated',
                           'sort_order': 'descending',
                           'portal_type': 'FeedFeederItem'}, batch=True)

        if not results and self.context.portal_type == 'Topic':
            # Use the queryCatalog of the Topic itself.
            results = self.context.queryCatalog(
                portal_type='FeedFeederItem')


        from Products.CMFPlone import Batch
        b_start = self.context.REQUEST.get('b_start', 0)
        b_size = 7
        batch = Batch(results, b_size, int(b_start), pagerange=1, orphan=0)

        result = []
        for index, x in enumerate(batch):
            content_url = x.getURL()
            item = dict(updated_date = x.getFeedItemUpdated,
                        url = content_url,
                        content_url = content_url,
                        title = x.Title,
                        summary = x.Description,
                        author = x.getFeedItemAuthor,
                        has_text = x.getHasBody,
                        target_link = x.getLink,
                        )
            self.extraDecoration(item, x)
            enclosures = x.getObjectids

            if (enclosures and enclosures is not None and
                len(enclosures) == 1):
                # only one enclosure? return item title but return link
                # to sole enclosure, unless there is some body text.
                if not int(x.getHasBody):
                    item['url'] = item['url'] + '/' + enclosures[0]

            result.append(item)

        return batch, result

    def __call__(self):
        # return Batch object for Plone batching controls
        # and internally use batched_item list when rendering this folder contents
        self.batch, self.batched_items = self.get_batched_items()
        return self.index(template_id='feed-folder.html')
