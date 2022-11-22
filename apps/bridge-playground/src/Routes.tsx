import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Routes, Route } from 'react-router-dom';
import { Helmet } from 'react-helmet';

import Home from './pages/Home';
import ViewContainer from './components/base/ViewContainer';

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
                                    <title>Home Page</title>
                                </Helmet>
                                <Home />
                            </>
                        }
                    />
                </Routes>
            </ViewContainer>
        </BrowserRouter>
    );
};

export default AppRouter;
