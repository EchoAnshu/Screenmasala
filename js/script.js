document.addEventListener("DOMContentLoaded", function () {

    const imageBase = "https://image.tmdb.org/t/p/w500";
    const backdropBase = "https://image.tmdb.org/t/p/original";

    function createCard(item) {
        const title = item.title || item.name || "Unknown";

        const poster = item.poster_path
            ? imageBase + item.poster_path
            : "assets/images/logo.png";

        const rating = item.vote_average
            ? item.vote_average.toFixed(1)
            : "N/A";

        const card = document.createElement("div");
        card.className = "movie-card";

        card.innerHTML = `
            <img src="${poster}" alt="${title}" loading="lazy"
                 onerror="this.onerror=null;this.src='assets/images/logo.png'">
            <div class="movie-info">
                <h3>${title}</h3>
                <p>⭐ ${rating}</p>
            </div>
        `;

        card.addEventListener("click", function () {
            const type = item.media_type || (item.title ? "movie" : "tv");

            window.location.href =
                "details.html?id=" + item.id + "&type=" + type;
        });

        return card;
    }

    async function loadData(url, row) {
        try {
            const response = await fetch(url);
            const data = await response.json();

            if (!response.ok || !Array.isArray(data.results)) {
                row.innerHTML =
                    '<p class="genre-loading">' +
                    "Unable to load titles. Please try again.</p>";
                return [];
            }

            row.innerHTML = "";

            const items = data.results.filter(function (item) {
                return item.poster_path;
            });

            items.forEach(function (item) {
                row.appendChild(createCard(item));
            });

            return items;

        } catch (error) {
            console.log(error);
            row.innerHTML =
                '<p class="genre-loading">' +
                "Unable to load titles. Check your connection.</p>";
            return [];
        }
    }

    const moviesRow = document.getElementById("moviesRow");
    const tvRow = document.getElementById("tvRow");
    const genreFilters = document.getElementById("genreFilters");
    const catalogTitle = document.getElementById("catalogTitle");

    async function loadGenrePage(type, row, filters) {
        const allUrl = type === "movie" ? "/api/movies" : "/api/tv";
        let activeGenre = "all";

        async function showTitles(url) {
            row.innerHTML = "<p class=\"genre-loading\">Loading titles...</p>";

            try {
                const response = await fetch(url);
                const data = await response.json();

                row.innerHTML = "";

                if (!response.ok || !Array.isArray(data.results)) {
                    row.textContent = "Unable to load titles. Please try again.";
                    return;
                }

                const visibleItems = data.results.filter(function (item) {
                    return item.poster_path;
                });

                if (visibleItems.length === 0) {
                    row.textContent = "No titles found for this genre.";
                    return;
                }

                visibleItems.forEach(function (item) {
                    row.appendChild(
                        createCard({ ...item, media_type: type })
                    );
                });

            } catch (error) {
                console.log(error);
                row.textContent = "Unable to load titles. Check your connection.";
            }
        }

        try {
            const response = await fetch("/api/genres?type=" + type);
            const data = await response.json();

            if (response.ok && Array.isArray(data.genres)) {
                filters.innerHTML = "";

                const allButton = document.createElement("button");
                allButton.type = "button";
                allButton.className = "genre-button active";
                allButton.textContent = "All";
                allButton.dataset.genre = "all";

                filters.appendChild(allButton);

                data.genres.forEach(function (genre) {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "genre-button";
                    button.textContent = genre.name;
                    button.dataset.genre = String(genre.id);

                    filters.appendChild(button);
                });
            }

        } catch (error) {
            console.log("Unable to load genres:", error);
        }

        filters.addEventListener("click", function (event) {
            const button = event.target.closest(".genre-button");

            if (!button) return;

            activeGenre = button.dataset.genre;

            filters.querySelectorAll(".genre-button").forEach(function (item) {
                item.classList.toggle("active", item === button);
            });

            if (catalogTitle) {
                catalogTitle.textContent = activeGenre === "all"
                    ? (type === "movie" ? "Popular Movies" : "Popular TV Shows")
                    : button.textContent +
                      (type === "movie" ? " Movies" : " TV Shows");
            }

            const url = activeGenre === "all"
                ? allUrl
                : "/api/genre?type=" + type +
                  "&genre_id=" + encodeURIComponent(activeGenre);

            showTitles(url);
        });

        await showTitles(allUrl);
    }

    if (moviesRow && genreFilters) {
        loadGenrePage("movie", moviesRow, genreFilters);

    } else if (tvRow && genreFilters) {
        loadGenrePage("tv", tvRow, genreFilters);

    } else {
        if (moviesRow) loadData("/api/movies", moviesRow);
        if (tvRow) loadData("/api/tv", tvRow);
    }

    const homeRows = document.querySelectorAll(".movie-row");

    if (!moviesRow && !tvRow && homeRows.length >= 3) {
        loadData("/api/trending", homeRows[0]);
        loadData("/api/movies", homeRows[1]);
        loadData("/api/tv", homeRows[2]);
    }

        const searchInput = document.getElementById("searchInput");
    const searchButton = document.getElementById("searchButton");
    const searchResults = document.getElementById("searchResults");
    const searchTitle = document.getElementById("searchTitle");

    async function performSearch() {
        const query = searchInput.value.trim();

        if (query === "") {
            alert("Please enter a movie or TV show name.");
            return;
        }

        try {
            const response = await fetch(
                "/api/search?query=" + encodeURIComponent(query)
            );

            const data = await response.json();

            searchResults.innerHTML = "";
            searchTitle.hidden = false;
            searchTitle.textContent = "Results for: " + query;

            if (!response.ok || !Array.isArray(data.results)) {
                searchResults.innerHTML =
                    "<p>Unable to search right now. Please try again.</p>";
                return;
            }

            const results = data.results.filter(function (item) {
                return item.media_type === "movie" ||
                       item.media_type === "tv";
            });

            if (results.length === 0) {
                searchResults.innerHTML = "<p>No results found.</p>";
                return;
            }

            results.forEach(function (item) {
                if (item.poster_path) {
                    searchResults.appendChild(createCard(item));
                }
            });

        } catch (error) {
            console.log(error);
            searchResults.innerHTML =
                "<p>Unable to search right now. Please try again.</p>";
            searchTitle.hidden = false;
            searchTitle.textContent = "Search failed";
        }
    }

    if (searchButton && searchInput) {
        searchButton.addEventListener("click", performSearch);

        searchInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                performSearch();
            }
        });

        const params = new URLSearchParams(window.location.search);
        const query = params.get("query");

        if (query) {
            searchInput.value = query;
            performSearch();
        }
    }

    const heroSearchForm = document.getElementById("heroSearchForm");

    if (heroSearchForm) {
        heroSearchForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const input = document.getElementById("heroSearchInput");
            const query = input.value.trim();

            if (query === "") {
                input.focus();
                return;
            }

            window.location.href =
                "search.html?query=" + encodeURIComponent(query);
        });
    }

    const loginButton = document.getElementById("loginButton");

    if (loginButton) {
        fetch("/api/user")
            .then(function (response) {
                return response.json();
            })
            .then(function (account) {
                if (!account.logged_in) return;

                loginButton.textContent = "Logout";
                loginButton.title = "Logout";

                loginButton.addEventListener("click", async function (event) {
                    event.preventDefault();

                    try {
                        await fetch("/api/logout");
                    } catch (error) {
                        console.log(error);
                    }

                    window.location.href = "index.html";
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    const detailsHero = document.getElementById("detailsHero");
    const similarMoviesRow = document.getElementById("similarMoviesRow");

    if (detailsHero) {
        loadDetails();
    }

    async function loadSimilar(id, type) {
        if (!similarMoviesRow) return;

        similarMoviesRow.innerHTML =
            "<p>Loading similar movies and shows...</p>";

        try {
            const response = await fetch(
                "/api/similar?id=" + encodeURIComponent(id) +
                "&type=" + encodeURIComponent(type)
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Similar titles request failed"
                );
            }

            const results = Array.isArray(data)
                ? data
                : data.results;

            similarMoviesRow.innerHTML = "";

            if (!Array.isArray(results) || results.length === 0) {
                similarMoviesRow.textContent = "No similar titles found.";
                return;
            }

            const visibleItems = results.filter(function (item) {
                return item.poster_path;
            });

            if (visibleItems.length === 0) {
                similarMoviesRow.textContent =
                    "No similar titles with posters found.";
                return;
            }

            visibleItems.forEach(function (item) {
                similarMoviesRow.appendChild(
                    createCard({
                        ...item,
                        media_type: item.media_type || type
                    })
                );
            });

        } catch (error) {
            console.error("Unable to load similar titles:", error);

            similarMoviesRow.textContent =
                "Unable to load similar titles. Please try again.";
        }
    }

    async function loadDetails() {
        const params = new URLSearchParams(window.location.search);
        const id = params.get("id");
        const type = params.get("type") || "movie";

        if (!id) {
            document.getElementById("detailsTitle").textContent =
                "Movie not found";
            return;
        }

        try {
            const response = await fetch(
                "/api/details?id=" + id + "&type=" + type
            );

            const item = await response.json();

            loadSimilar(id, type);

            const title = item.title || item.name || "Unknown";

            const date =
                item.release_date ||
                item.first_air_date ||
                "N/A";

            const genres = item.genres
                ? item.genres.map(function (genre) {
                    return genre.name;
                }).join(", ")
                : "N/A";

            document.title = title + " - ScreenMasala";

            document.getElementById("detailsTitle").textContent = title;

            document.getElementById("detailsType").textContent =
                type === "tv" ? "TV SHOW" : "MOVIE";

            document.getElementById("detailsMeta").textContent =
                date.substring(0, 4) +
                "  •  ⭐ " +
                (item.vote_average
                    ? item.vote_average.toFixed(1)
                    : "N/A");

            document.getElementById("detailsGenres").textContent = genres;

            document.getElementById("detailsDescription").textContent =
                item.overview || "No description available.";

            document.getElementById("detailsPoster").src =
                item.poster_path
                    ? imageBase + item.poster_path
                    : "assets/images/logo.png";

            if (item.backdrop_path) {
                detailsHero.style.backgroundImage =
                    "url('" + backdropBase + item.backdrop_path + "')";
            }

            document.getElementById("aboutRating").textContent =
                item.vote_average
                    ? item.vote_average.toFixed(1) + " / 10"
                    : "N/A";

            document.getElementById("aboutDate").textContent = date;

            document.getElementById("aboutLanguage").textContent =
                item.original_language
                    ? item.original_language.toUpperCase()
                    : "N/A";

            document.getElementById("aboutType").textContent =
                type === "tv" ? "TV Show" : "Movie";

            const watchlistButton =
                document.getElementById("watchlistButton");

            if (watchlistButton) {
                watchlistButton.addEventListener("click", async function () {
                    try {
                        const response = await fetch("/api/watchlist", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                tmdb_id: item.id,
                                title: title,
                                poster: item.poster_path
                                    ? imageBase + item.poster_path
                                    : "",
                                media_type: type
                            })
                        });

                        const data = await response.json();

                        if (response.status === 401) {
                            alert("Please login first.");
                            window.location.href = "login.html";
                            return;
                        }

                        alert(data.message || "Added to watchlist.");

                    } catch (error) {
                        console.log(error);
                        alert("Unable to add to watchlist.");
                    }
                });
            }

        } catch (error) {
            console.log(error);

            document.getElementById("detailsTitle").textContent =
                "Unable to load details";
        }
    }

        const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const name =
                document.getElementById("registerName").value.trim();

            const email =
                document.getElementById("registerEmail").value.trim();

            const password =
                document.getElementById("registerPassword").value;

            const confirm =
                document.getElementById("registerConfirm").value;

            if (name === "" || email === "" ||
                password === "" || confirm === "") {
                alert("Please fill all fields.");
                return;
            }

            if (password !== confirm) {
                alert("Passwords do not match.");
                return;
            }

            try {
                const response = await fetch("/api/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password
                    })
                });

                const data = await response.json();

                alert(data.message);

                if (data.success) {
                    window.location.href = "login.html";
                }

            } catch (error) {
                console.log(error);

                alert(
                    "Unable to connect to the server. Make sure Flask is running."
                );
            }
        });
    }

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const email =
                document.getElementById("loginEmail").value.trim();

            const password =
                document.getElementById("loginPassword").value;

            if (email === "" || password === "") {
                alert("Please enter email and password.");
                return;
            }

            try {
                const response = await fetch("/api/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });

                const data = await response.json();

                alert(data.message || "Login successful.");

                if (data.success) {
                    window.location.href = "profile.html";
                }

            } catch (error) {
                console.log(error);

                alert(
                    "Unable to connect to the server. Make sure Flask is running."
                );
            }
        });
    }

    const profilePage = document.getElementById("profilePage");
    const logoutButton = document.getElementById("logoutButton");

    if (profilePage) {
        loadProfile();
    }

    if (logoutButton) {
        logoutButton.addEventListener("click", async function () {
            try {
                await fetch("/api/logout");
            } catch (error) {
                console.log(error);
            }

            window.location.href = "index.html";
        });
    }

    async function loadProfile() {
        try {
            const response = await fetch("/api/user");
            const account = await response.json();

            if (!account.logged_in) {
                window.location.href = "login.html";
                return;
            }

            document.title = account.name + " - ScreenMasala";

            document.getElementById("profileName").textContent = account.name;

            document.getElementById("profileAvatar").textContent =
                account.name.trim().charAt(0).toUpperCase();

            document.getElementById("profileInfoName").textContent =
                account.name;

            document.getElementById("profileEmail").textContent =
                account.email;

            document.getElementById("profileSince").textContent =
                account.member_since || "N/A";

            try {
                const watchlistResponse = await fetch("/api/watchlist");
                const items = await watchlistResponse.json();

                document.getElementById("profileWatchlistCount").textContent =
                    Array.isArray(items) ? String(items.length) : "0";

            } catch (error) {
                console.log(error);
                document.getElementById("profileWatchlistCount")
                    .textContent = "0";
            }

        } catch (error) {
            console.log(error);
        }
    }

    const watchlistContainer =
        document.getElementById("watchlistContainer");

    if (watchlistContainer) {
        loadWatchlist();
    }

    async function loadWatchlist() {
        try {
            const response = await fetch("/api/watchlist");

            const data = await response.json();

            if (response.status === 401) {
                watchlistContainer.innerHTML = `
                    <div class="watchlist-login">
                        <h2>Please Login</h2>
                        <p>Login to see and manage your watchlist.</p>
                        <a href="login.html">Login</a>
                    </div>
                `;
                return;
            }

            watchlistContainer.innerHTML = "";

            if (data.length === 0) {
                watchlistContainer.innerHTML = `
                    <div class="watchlist-empty">
                        <h2>Your watchlist is empty</h2>
                        <p>Add movies and TV shows you want to watch later.</p>
                        <a href="movies.html">Explore Movies</a>
                    </div>
                `;
                return;
            }

            data.forEach(function (item) {
                const card = document.createElement("div");

                card.className = "watchlist-card";

                card.innerHTML = `
                    <img src="${item.poster || "assets/images/logo.png"}" alt="${item.title}" loading="lazy"
                         onerror="this.onerror=null;this.src='assets/images/logo.png'">
                    <div class="watchlist-info">
                        <h3>${item.title}</h3>
                        <p>${item.media_type === "tv" ? "TV Show" : "Movie"}</p>
                        <div class="watchlist-buttons">
                            <button class="watch-button">Watch</button>
                            <button class="remove-button">Remove</button>
                        </div>
                    </div>
                `;

                card.querySelector(".watch-button")
                    .addEventListener("click", function () {
                        window.location.href =
                            "details.html?id=" +
                            item.tmdb_id +
                            "&type=" +
                            item.media_type;
                    });

                card.querySelector(".remove-button")
                    .addEventListener("click", async function () {
                        try {
                            const response = await fetch(
                                "/api/watchlist",
                                {
                                    method: "DELETE",
                                    headers: {
                                        "Content-Type": "application/json"
                                    },
                                    body: JSON.stringify({
                                        id: item.id
                                    })
                                }
                            );

                            const result = await response.json();

                            if (result.success) {
                                card.remove();

                                if (watchlistContainer.children.length === 0) {
                                    loadWatchlist();
                                }
                            }

                        } catch (error) {
                            console.log(error);
                        }
                    });

                watchlistContainer.appendChild(card);
            });

        } catch (error) {
            console.log(error);

            watchlistContainer.innerHTML =
                "<p>Unable to load watchlist.</p>";
        }
    }

});