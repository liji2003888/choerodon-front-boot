/*eslint-disable*/
import React, { Component } from 'react';
import { render } from 'react-dom';
import { HashRouter as Router, Route, Switch } from 'react-router-dom';
import { createBrowserHistory } from 'history';
import { LocaleProvider } from 'choerodon-ui';
import { useStrict } from 'mobx';
import { observer, Provider } from 'mobx-react';
import stores from '../lib/containers/stores';
import AppState from '../lib/containers/stores/AppState';
import asyncRouter from '../lib/containers/components/util/asyncRouter';
import asyncLocaleProvider from '../lib/containers/components/util/asyncLocaleProvider';
import asyncPropsLoader from '../lib/containers/components/util/asyncPropsLoader';

const Masters = asyncRouter(() => import('../lib/containers/components/master'), () => import('{{ routesPath }}'));

@observer
class App extends Component {

  componentWillMount() {
    this.handleAuth();
  }

  handleAuth = () => {
    let token = Choerodon.getAccessToken(window.location.hash);
    if (token) {
      Choerodon.setAccessToken(token, 60 * 60);
    }
    AppState.loadUserInfo().then(data => {
      AppState.setUserInfo(data);
    });
  };

  render() {
    const langauge = AppState.currentLanguage;
    const IntlProviderAsync = asyncLocaleProvider(langauge, () => import(`../lib/containers/locale/${langauge}`), () => import(`react-intl/locale-data/${langauge.split('_')[0]}`));
    const LocaleProviderAsync = asyncPropsLoader(LocaleProvider,
      import(`choerodon-ui/es/locale-provider/${langauge}.js`).then(({ default: locale }) => ({ locale })));
    return (
      <LocaleProviderAsync>
        <IntlProviderAsync>
          <Provider {...stores}>
            <div>
              <Router hashHistory={createBrowserHistory}>
                <Switch>
                  <Route path='/' component={Masters} />
                </Switch>
              </Router>
            </div>
          </Provider>
        </IntlProviderAsync>
      </LocaleProviderAsync>
    );
  }
}

useStrict(true);

render(<App />, document.getElementById('app'));