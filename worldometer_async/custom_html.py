from requests_html import (
    HTML,
    DEFAULT_ENCODING,
    DEFAULT_URL,
    MaxRetries,
    HTMLResponse,
    BaseSession,
    HTMLSession,
    AsyncHTMLSession,
)
from typing import Union
import pyppeteer


class HTML(HTML):
    async def arender(
        self,
        retries: int = 8,
        script: str = None,
        wait: float = 0.2,
        scrolldown=False,
        sleep: float = 0.5,
        reload: bool = True,
        timeout: Union[float, int] = 8.0,
        keep_page: bool = False,
    ):
        """Async version of render. Takes same parameters."""

        self.browser = await self.session.browser
        content = None

        # Automatically set Reload to False, if example URL is being used.
        if self.url == DEFAULT_URL:
            reload = False

        for _ in range(retries):
            if not content:
                try:

                    content, result, page = await self._async_render(
                        url=self.url,
                        script=script,
                        sleep=sleep,
                        wait=wait,
                        content=self.html,
                        reload=reload,
                        scrolldown=scrolldown,
                        timeout=timeout,
                        keep_page=keep_page,
                    )
                except TypeError:
                    pass
            else:
                break

        if not content:
            raise MaxRetries("Unable to render the page. Try increasing timeout")

        html = HTML(
            url=self.url,
            html=content.encode(DEFAULT_ENCODING),
            session=self.session,
            default_encoding=DEFAULT_ENCODING,
        )
        self.__dict__.update(html.__dict__)
        self.page = page
        return result


class HTMLResponse(HTMLResponse):
    @property
    def html(self) -> HTML:
        if not self._html:
            self._html = HTML(
                session=self.session,
                url=self.url,
                html=self.content,
                default_encoding=self.encoding,
            )

        return self._html


class BaseSession(BaseSession):
    def response_hook(self, response, **kwargs) -> HTMLResponse:
        """Change response enconding and replace it by a HTMLResponse."""
        if not response.encoding:
            response.encoding = DEFAULT_ENCODING
        return HTMLResponse._from_response(response, self)

    @property
    async def browser(self, ex_path: str = "/usr/bin/google-chrome"):
        if not hasattr(self, "_browser"):
            self._browser = await pyppeteer.launch(
                ignoreHTTPSErrors=not (self.verify),
                headless=True,
                args=self.__browser_args,
                executablePath=ex_path,
            )

        return self._browser


class HTMLSession(HTMLSession, BaseSession): ...


class AsyncHTMLSession(AsyncHTMLSession, BaseSession): ...
