// Store JavaScript
document.addEventListener("DOMContentLoaded", () => {
  initializeStore()
})

function initializeStore() {
  setupEventListeners()
  setupFilters() // Declare setupFilters function
  setupCategoryTabs()
  animateCards()
}

function setupEventListeners() {
  // Search functionality
  const searchInput = document.getElementById("searchInput")
  if (searchInput) {
    searchInput.addEventListener("input", debounce(filterOffers, 300))
  }

  // Filter dropdowns
  const categoryFilter = document.getElementById("categoryFilter")
  const sortFilter = document.getElementById("sortFilter")

  if (categoryFilter) {
    categoryFilter.addEventListener("change", filterOffers)
  }

  if (sortFilter) {
    sortFilter.addEventListener("change", sortOffers)
  }

  // Close modals on escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const modals = document.querySelectorAll(".modal.show")
      modals.forEach((modal) => {
        const bsModal = window.bootstrap.Modal.getInstance(modal) // Declare bootstrap variable
        if (bsModal) bsModal.hide()
      })
    }
  })
}

function setupFilters() {
  // Placeholder for filter setup logic
}

function setupCategoryTabs() {
  const categoryTabs = document.querySelectorAll("#categoryTabs .nav-link")

  categoryTabs.forEach((tab) => {
    tab.addEventListener("click", function (e) {
      e.preventDefault()

      // Update active tab
      categoryTabs.forEach((t) => t.classList.remove("active"))
      this.classList.add("active")

      // Filter by category
      const category = this.getAttribute("data-category")
      filterByCategory(category)
    })
  })
}

function filterByCategory(category) {
  const offers = document.querySelectorAll(".offer-card")
  let visibleCount = 0

  offers.forEach((offer) => {
    const offerCategory = offer.getAttribute("data-category")

    if (category === "all" || offerCategory === category) {
      offer.style.display = "block"
      visibleCount++
    } else {
      offer.style.display = "none"
    }
  })

  // Update category filter dropdown
  const categoryFilter = document.getElementById("categoryFilter")
  if (categoryFilter) {
    categoryFilter.value = category
  }

  toggleEmptyState(visibleCount === 0)
  animateVisibleCards()
}

function filterOffers() {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase()
  const categoryFilter = document.getElementById("categoryFilter").value
  const offers = document.querySelectorAll(".offer-card")
  let visibleCount = 0

  offers.forEach((offer) => {
    const name = offer.getAttribute("data-name")
    const category = offer.getAttribute("data-category")

    const matchesSearch = name.includes(searchTerm)
    const matchesCategory = categoryFilter === "all" || category === categoryFilter

    if (matchesSearch && matchesCategory) {
      offer.style.display = "block"
      visibleCount++
    } else {
      offer.style.display = "none"
    }
  })

  toggleEmptyState(visibleCount === 0)
  animateVisibleCards()
}

function sortOffers() {
  const sortBy = document.getElementById("sortFilter").value
  const offersGrid = document.getElementById("offersGrid")
  const offers = Array.from(document.querySelectorAll(".offer-card"))

  offers.sort((a, b) => {
    switch (sortBy) {
      case "name":
        return a.getAttribute("data-name").localeCompare(b.getAttribute("data-name"))
      case "coins_asc":
        return Number.parseInt(a.getAttribute("data-coins")) - Number.parseInt(b.getAttribute("data-coins"))
      case "coins_desc":
        return Number.parseInt(b.getAttribute("data-coins")) - Number.parseInt(a.getAttribute("data-coins"))
      case "stock":
        return Number.parseInt(b.getAttribute("data-stock")) - Number.parseInt(a.getAttribute("data-stock"))
      default:
        return 0
    }
  })

  // Re-append sorted offers
  offers.forEach((offer) => offersGrid.appendChild(offer))
  animateVisibleCards()
}

function toggleEmptyState(show) {
  const emptyState = document.getElementById("emptyState")
  if (emptyState) {
    emptyState.style.display = show ? "block" : "none"
  }
}

function animateCards() {
  const offers = document.querySelectorAll(".offer-card")
  offers.forEach((offer, index) => {
    offer.style.animationDelay = `${index * 0.1}s`
  })
}

function animateVisibleCards() {
  const visibleOffers = document.querySelectorAll('.offer-card[style*="block"], .offer-card:not([style*="none"])')
  visibleOffers.forEach((offer, index) => {
    offer.style.animation = "none"
    setTimeout(() => {
      offer.style.animation = `fadeIn 0.5s ease forwards`
      offer.style.animationDelay = `${index * 0.1}s`
    }, 10)
  })
}

// Redeem functionality
function redeemOffer(offerId, offerName, coinsRequired) {
  const currentCoins = Number.parseInt(document.querySelector(".coin-amount").textContent)
  const afterRedemption = currentCoins - coinsRequired

  // Update modal content
  document.getElementById("redeemOfferName").textContent = offerName
  document.getElementById("afterRedemption").textContent = afterRedemption

  // Store offer data for confirmation
  const confirmBtn = document.getElementById("confirmRedeem")
  confirmBtn.setAttribute("data-offer-id", offerId)
  confirmBtn.setAttribute("data-coins-required", coinsRequired)

  // Show modal
  const modal = new window.bootstrap.Modal(document.getElementById("redeemModal"))
  modal.show()
}

// Confirm redemption
document.getElementById("confirmRedeem").addEventListener("click", function () {
  const offerId = this.getAttribute("data-offer-id")
  const coinsRequired = Number.parseInt(this.getAttribute("data-coins-required"))

  // Show loading
  showLoading()

  // Hide modal
  const modal = window.bootstrap.Modal.getInstance(document.getElementById("redeemModal"))
  modal.hide()

  // Simulate API call
  setTimeout(() => {
    // Redirect to redemption page
    window.location.href = `/store/redeem/${offerId}/`
  }, 1500)
})

// Wishlist functionality
function toggleWishlist(offerId) {
  const button = event.target.closest("button")
  const icon = button.querySelector("i")

  if (icon.classList.contains("far")) {
    icon.classList.remove("far")
    icon.classList.add("fas", "wishlist-active")
    showToast("Added to wishlist!", "success")
  } else {
    icon.classList.remove("fas", "wishlist-active")
    icon.classList.add("far")
    showToast("Removed from wishlist", "info")
  }

  // Here you would typically make an API call to update the wishlist
  // fetch(`/api/wishlist/toggle/${offerId}/`, { method: 'POST' })
}

// Quick view functionality
function quickView(offerId) {
  const modal = new window.bootstrap.Modal(document.getElementById("quickViewModal"))
  const content = document.getElementById("quickViewContent")

  // Show loading in modal
  content.innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-spinner fa-spin fa-2x text-primary"></i>
            <p class="mt-2">Loading offer details...</p>
        </div>
    `

  modal.show()

  // Simulate API call for offer details
  setTimeout(() => {
    content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <img src="/placeholder.svg?height=300&width=400" class="img-fluid rounded" alt="Offer Image">
                </div>
                <div class="col-md-6">
                    <h4>Offer Details</h4>
                    <p>This is a detailed view of the selected offer. Here you can see all the information about the offer including terms and conditions.</p>
                    <div class="offer-stats">
                        <div class="stat-item">
                            <i class="fas fa-coins text-warning"></i>
                            <span>100 coins required</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-map-marker-alt text-danger"></i>
                            <span>Downtown Store</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-calendar text-success"></i>
                            <span>Valid until Dec 31, 2024</span>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-primary" onclick="redeemOffer(${offerId}, 'Sample Offer', 100)">
                            <i class="fas fa-shopping-cart"></i> Redeem Now
                        </button>
                    </div>
                </div>
            </div>
        `
  }, 1000)
}

// Utility functions
function showLoading() {
  document.getElementById("loadingOverlay").style.display = "flex"
}

function hideLoading() {
  document.getElementById("loadingOverlay").style.display = "none"
}

function showToast(message, type = "success") {
  // Create toast element
  const toast = document.createElement("div")
  toast.className = `toast-notification toast-${type}`
  toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === "success" ? "check-circle" : "info-circle"}"></i>
            <span>${message}</span>
        </div>
    `

  // Add to page
  document.body.appendChild(toast)

  // Show toast
  setTimeout(() => toast.classList.add("show"), 100)

  // Remove toast
  setTimeout(() => {
    toast.classList.remove("show")
    setTimeout(() => document.body.removeChild(toast), 300)
  }, 3000)
}

function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Add toast notification styles
const toastStyles = `
    .toast-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.175);
        padding: 1rem 1.5rem;
        z-index: 9999;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        border-left: 4px solid;
    }
    
    .toast-notification.show {
        transform: translateX(0);
    }
    
    .toast-notification.toast-success {
        border-left-color: #28a745;
    }
    
    .toast-notification.toast-info {
        border-left-color: #17a2b8;
    }
    
    .toast-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .toast-content i {
        color: inherit;
    }
`

// Add styles to head
const styleSheet = document.createElement("style")
styleSheet.textContent = toastStyles
document.head.appendChild(styleSheet)

// Declare bootstrap variable
window.bootstrap = window.bootstrap || {}
