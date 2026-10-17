(() => {
  const search = document.getElementById('dashboardAppSearch');
  const status = document.getElementById('dashboardAppSearchStatus');
  const apps = Array.from(document.querySelectorAll('.dashboard-app'));

  if (!search || !status || apps.length === 0) return;

  const updateSections = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visibleApps = 0;
    let visibleModels = 0;

    apps.forEach((app) => {
      const appName = app.querySelector('summary h3')?.textContent.trim().toLocaleLowerCase() || '';
      const appMatches = query !== '' && appName.includes(query);
      const rows = Array.from(app.querySelectorAll('li[data-model-name]'));
      let appVisibleModels = 0;

      rows.forEach((row) => {
        const matches = query === '' || appMatches || row.dataset.modelName.includes(query);
        row.hidden = !matches;
        if (matches) appVisibleModels += 1;
      });

      const visible = query === '' || appMatches || appVisibleModels > 0;
      app.hidden = !visible;
      app.open = query !== '' && visible;
      if (visible) visibleApps += 1;
      visibleModels += appVisibleModels;
    });

    status.textContent = query
      ? `${visibleModels} section${visibleModels === 1 ? '' : 's'} found in ${visibleApps} app${visibleApps === 1 ? '' : 's'}.`
      : '';
  };

  search.addEventListener('input', updateSections);
})();
