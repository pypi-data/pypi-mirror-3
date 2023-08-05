from zope.formlib.itemswidgets import DropdownWidget, EXPLICIT_EMPTY_SELECTION


class GroupedDropdownWidget(DropdownWidget):
    """Variation of the DropdownWidget that provides grouped options."""

    def renderItemsWithValues(self, values):
        """Render the grouped list of possible values, with those found in
        `values` being marked as selected."""

        cssClass = self.cssClass

        # multiple items with the same value are not allowed from a
        # vocabulary, so that need not be considered here
        rendered_items = []
        count = 0

        # Handle case of missing value
        missing = self._toFormValue(self.context.missing_value)

        if self._displayItemForMissingValue and (
            not self.context.required or
            EXPLICIT_EMPTY_SELECTION and
            self.explicit_empty_selection and
            missing in values and
            self.context.default is None):

            if missing in values:
                render = self.renderSelectedItem
            else:
                render = self.renderItem

            missing_item = render(count,
                self.translate(self._messageNoValue),
                missing,
                self.name,
                cssClass)
            rendered_items.append(missing_item)
            count += 1

        if missing in values and self.context.default is not None:
            values = [self.context.default]

        # Render grouped values
        groups = self.context.groups.groups(self.vocabulary)
        for group, terms in groups:
            rendered_items.append('<optgroup label="%s">' % self.translate(group))
            for term in terms:
                item_text = self.textForValue(term)

                if term.value in values:
                    render = self.renderSelectedItem
                else:
                    render = self.renderItem

                rendered_item = render(count,
                    item_text,
                    term.token,
                    self.name,
                    cssClass)

                rendered_items.append(rendered_item)
                count += 1
            rendered_items.append('</optgroup>')

        return rendered_items
