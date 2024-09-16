# Import functions and libraries
import requests
from bs4 import BeautifulSoup
import random
import time

# Headers to mimic a browser request
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# A function to scrape categories from Chartable
def scrape_categories(url):
    while True:
        try:
            response = requests.get(url, headers=headers)

            # If we get a 429 error (rate limiting), wait and retry
            if response.status_code == 429:
                print("Rate limit hit. Sleeping for a bit...")
                time.sleep(10)
                continue

            if response.status_code != 200:
                print(f"Failed to get the webpage: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract categories and links
            main_div = soup.find('div', class_='mb3 f4')
            if not main_div:
                print("Main div not found.")
                return None

            # Create a dictionary to store category data
            category_data = {}

            a_tags = main_div.find_all('a', class_='link blue')
            for a_tag in a_tags:
                full_name = a_tag.get_text(strip=True)

            # Extract the words between "Top" and "podcasts"
                name = full_name.split("Top")[1].split("podcasts")[0].strip().lower()  # Convert to lowercase

                link = a_tag['href']
                category_data[name] = link

            return category_data

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

# A function to get top 3 podcasts for a selected category
def get_top_podcasts_from_category(category, category_data, retry_attempts=0):
    if category not in category_data:
        raise KeyError(f"""Category '{category}' is not available. Please choose from the following list of categories and try again.
        {list(category_data.keys())}""")

    url = category_data[category]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        podcast_rows = soup.find_all("tr", class_="striped--near-white")
        top_podcasts = []

        for row in podcast_rows[:3]:
            try:
                rank = row.find("td", class_="pv2 ph1 w3").text.strip()
                title = row.find("a", class_="link blue").text.strip()
                link = row.find("a", class_="link blue").get("href")
                top_podcasts.append((rank, title, link))
            except AttributeError:
                print(f"One of the elements was not found, skipping this row.")

        return top_podcasts
    elif response.status_code == 429:
        if retry_attempts < 5:  # Limit retries to prevent infinite loops
            retry_attempts += 1
            wait_time = 2 ** retry_attempts
            print(f"Too many requests. Waiting for {wait_time} seconds before trying again.")
            time.sleep(wait_time)
            return get_top_podcasts_from_category(category, retry_attempts)  # Retry after delay
        else:
            print("Max retry attempts reached. Please try again later.")
            return []
    else:
        print(f"Failed to retrieve data for {category}. Status Code: {response.status_code}")
        return []

# Main function to handle user input and display top podcasts
def get_podcasts(url):
    if __name__ == "__main__":
        categories = scrape_categories(url)

        # This just provides information to the user about how many categories there are, and the category names
        if categories:
            print(f"Found {len(categories)} categories.")
            category_list = list(categories.keys())
            category_list[0] = category_list[0].capitalize() # capitalize the first category so when printed, it looks nice
            print(f"These are the available categories: \n{', '.join(category_list)}.")
        else:
            print("No categories found.")
        category = input(f"\nEnter the podcast category (e.g., comedy, business, news): ").strip()
        top_podcasts = get_top_podcasts_from_category(category, categories)

        if top_podcasts:
            for podcast in top_podcasts:
                print(f"\nRank {podcast[0]}: {podcast[1]} - {podcast[2]}")
        else:
            print("No podcasts found for the selected category.")

url = "https://chartable.com/charts/spotify/us"
get_podcasts(url)