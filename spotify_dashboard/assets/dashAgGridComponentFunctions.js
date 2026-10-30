var dagfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

dagfuncs.AlbumCover = function (params) {
    if (!params.value) {
        return null;
    }
    return React.createElement('img', {
        src: params.value,
        alt: '',
        style: {
            height: '36px',
            width: '36px',
            objectFit: 'cover',
            borderRadius: '4px',
            display: 'block',
        },
    });
};

dagfuncs.EnergyBar = function (params) {
    var energy = Number(params.value);
    if (isNaN(energy)) {
        energy = 0;
    }
    var pct = Math.max(0, Math.min(1, energy)) * 100;
    return React.createElement(
        'div',
        { style: { display: 'flex', alignItems: 'center', gap: '8px', width: '100%' } },
        React.createElement(
            'div',
            {
                style: {
                    flex: 1,
                    height: '10px',
                    background: 'rgb(50, 50, 50)',
                    borderRadius: '5px',
                    overflow: 'hidden',
                },
            },
            React.createElement('div', {
                style: {
                    width: pct + '%',
                    height: '100%',
                    background: 'rgb(30, 195, 90)',
                },
            })
        ),
        React.createElement('span', { style: { minWidth: '34px', textAlign: 'right' } }, energy.toFixed(2))
    );
};
