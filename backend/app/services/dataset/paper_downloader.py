import os
import requests


class PaperDownloader:

    def __init__(self, download_dir: str):

        self.download_dir = download_dir

        os.makedirs(
            self.download_dir,
            exist_ok=True
        )

    def download_paper(self, paper: dict):

        pdf_url = paper["pdf_url"]

        paper_id = paper["id"]

        file_path = os.path.join(
            self.download_dir,
            f"{paper_id}.pdf"
        )

        if os.path.exists(file_path):

            print(f"Already exists: {paper_id}")

            return file_path

        try:

            response = requests.get(
                pdf_url,
                timeout=60
            )

            response.raise_for_status()

            with open(
                file_path,
                "wb"
            ) as f:

                f.write(response.content)

            print(f"Downloaded: {paper_id}")

            return file_path

        except Exception as e:

            print(f"Failed: {paper_id}")

            print(e)

            return None

    def download_papers(self, papers):

        downloaded = []

        for paper in papers:

            path = self.download_paper(
                paper
            )

            if path:

                downloaded.append(
                    {
                        "paper": paper,
                        "pdf_path": path
                    }
                )

        return downloaded