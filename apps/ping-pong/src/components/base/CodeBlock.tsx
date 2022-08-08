import React from 'react';
import Highlight, { defaultProps } from 'prism-react-renderer';
import theme from 'prism-react-renderer/themes/nightOwl';
import styled from '@emotion/styled';

export const Pre = styled.pre`
    text-align: left;
    margin: 1em 0;
    padding: 0.5em;
    border-radius: 10px;
    overflow-x: auto;

    & .token-line {
        line-height: 1.3em;
        height: 1.3em;
    }
`;

interface OwnProps {
    code: string;
    language: 'json';
}

const CodeBlock: React.FC<OwnProps> = ({ ...props }) => (
    <Highlight {...{ ...defaultProps, ...props }} theme={theme}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
            <Pre className={className} style={style}>
                {tokens.map((line, i) => (
                    <div {...getLineProps({ line, key: i })}>
                        {line.map((token, key) => (
                            <span {...getTokenProps({ token, key })} />
                        ))}
                    </div>
                ))}
            </Pre>
        )}
    </Highlight>
);

export default CodeBlock;
