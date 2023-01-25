import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Routes, Route } from 'react-router-dom';
import { Helmet } from 'react-helmet';

import Bridge from './pages/Bridge';
import ViewContainer from './components/base/ViewContainer';
import Crowdfund from './pages/Crowdfund';

const AppRouter: React.FC = () => {
    return (
        <BrowserRouter basename={process.env.PUBLIC_URL}>
            <ViewContainer>
                <Routes>
                    <Route
                        path="/"
                        element={
                            <>
                                <Helmet>
                                    <title>Crowdfund example</title>
                                </Helmet>
                                <Crowdfund />
                            </>
                        }
                    />
                    <Route
                        path="/bridge"
                        element={
                            <>
                                <Helmet>
                                    <title>Bridge example</title>
                                </Helmet>
                                <Bridge />
                            </>
                        }
                    />
                    <Route
                        path="/crowdfund"
                        element={
                            <>
                                <Helmet>
                                    <title>Crowdfund example</title>
                                </Helmet>
                                <Crowdfund />
                            </>
                        }
                    />
                </Routes>
            </ViewContainer>
        </BrowserRouter>
    );
};

export default AppRouter;
