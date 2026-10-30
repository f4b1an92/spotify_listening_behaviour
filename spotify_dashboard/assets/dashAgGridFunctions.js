var dagfuncs = (window.dashAgGridFunctions = window.dashAgGridFunctions || {});

// Compares the picked date with a 'YYYY-MM-DD' cell value for agDateColumnFilter
dagfuncs.dateComparator = function (filterDate, cellValue) {
    if (!cellValue) {
        return -1;
    }
    var parts = String(cellValue).slice(0, 10).split('-');
    var cellDate = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    if (cellDate < filterDate) {
        return -1;
    }
    return cellDate > filterDate ? 1 : 0;
};
