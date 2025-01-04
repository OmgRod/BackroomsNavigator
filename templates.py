class HTMLTemplates:
    @staticmethod
    def generate_html_template(name, html_content):
        return f'''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>Backrooms Navigator - {name}</title>
                <meta property="og:title" content="Backrooms Navigator - {name}">
                <meta property="og:description" content="Navigate through the mysterious levels of the Backrooms.">
                <meta property="og:image" content="/assets/promo.png">
                <meta property="og:type" content="website">
                <meta property="og:url" content="http://localhost:8050">
                <style>
                    html, body {{
                        height: 100%;
                        margin: 0;
                        overflow: hidden;
                    }}
                    #graph > div {{
                        height: 100%;
                        width: 100%;
                        position: absolute;
                    }}
                </style>
            </head>
            <body>
                <div id="graph">{html_content}</div>
            </body>
        </html>
        '''