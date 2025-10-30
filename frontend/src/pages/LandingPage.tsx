import { Link } from 'react-router-dom'
import { Target, Zap, TrendingUp, Search } from 'lucide-react'

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-between items-center">
          <span className="text-3xl font-bold text-primary-600">Genie</span>
          <Link
            to="/dashboard"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Your AI-Powered
            <span className="text-primary-600"> Opportunity Scout</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Discover relevant career, speaking, and growth opportunities tailored to
            your goals. Let Genie continuously search and notify you of new
            opportunities.
          </p>
          <Link
            to="/goals/new"
            className="inline-flex items-center px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
          >
            <Target className="w-5 h-5 mr-2" />
            Create Your First Goal
          </Link>
        </div>

        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <Search className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Smart Discovery</h3>
            <p className="text-gray-600">
              AI-powered search across multiple sources to find opportunities that
              match your unique goals.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Continuous Updates</h3>
            <p className="text-gray-600">
              Get notified automatically when new relevant opportunities are found.
              Never miss out again.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Personalized Ranking</h3>
            <p className="text-gray-600">
              Learn from your feedback to show you the most relevant opportunities
              first.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default LandingPage

