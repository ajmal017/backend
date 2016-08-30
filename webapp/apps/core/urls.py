from django.conf.urls import url
from core import views

urlpatterns = [
    url(r'^leader/profile/funds/$', views.LeaderFunds.as_view(), name='funds-leader-profile'),
    url(r'^leader/board/$', views.LeaderBoard.as_view(), name='leader-board'),
    url(r'^(?P<type>^[a-z]+)/response/add/$', views.AssessAnswerNew.as_view(), name='assess-answers-add'),
    url(r'^recommended/portfolios/$', views.RecommendedPortfolios.as_view(), name='recommended-portfolios'),
    url(r'^(?P<fund_id>^[0-9]+)/schema/fact-sheet/$', views.SchemaFactSheet.as_view(), name='schema-fact-sheet'),
    url(r'^assess/new/response/add/$', views.AssessAnswer.as_view(), name='assess-new-answers-add'),
    url(r'^retirement/new/response/add/$', views.RetirementAnswer.as_view(), name='retirement-new-answers-add'),
    url(r'^invest/new/response/add/$', views.InvestAnswer.as_view(), name='invest-new-answers-add'),
    url(r'^tax/new/response/add/$', views.TaxAnswer.as_view(), name='tax-new-answers-add'),
    url(r'^(?P<type>^[a-z]+)/new/response/add/$', views.GenericGoalAnswer.as_view(), name='generic-answers-add'),
    url(r'^save/email/$', views.SaveEmail.as_view(), name='save-email'),
    url(r'^funds/get/all/$', views.FundsDividedIntoCategories.as_view(), name='fund-get-all'),
    url(r'^funds/compare/$', views.FundsComparedData.as_view(), name='fund-data-comprison'),
    url(r'^portfolio/performance/$', views.PortfolioPerformance.as_view(), name='portfolio-performance'),
    url(r'^fund/historic/performance/$', views.FundHistoricPerformance.as_view(), name='fund-historic-performance'),
    url(r'^review/card/$', views.ReviewCard.as_view(), name='review-card'),
    url(r'^funds/comparison/$', views.FundsHistoricComparison.as_view(), name='funds-historic-comparison'),
    url(r'^popular/funds/get/$', views.PopularFunds.as_view(), name='get-popular-funds'),
    url(r'^portfolio/historic/performance/', views.PortfolioHistoricPerformance.as_view(),
        name='portfolio-historic-performance'),
    url(r'^transaction/history/$', views.TransactionHistoryNew.as_view(), name='transaction-history-new'),
    url(r'^invested/fund/get/$', views.GetInvestedFundReturn.as_view(), name='fund-return'),
    url(r'^fund/redeem/add/new/$', views.FundRedeem.as_view(), name='fund_redeem_add'),
    url(r'^dashboard/portfolio/historic/performance/$', views.DashboardPortfolioHistoricPerformance.as_view(),
        name='dashboard-portfolio-historic-performance'),
    url(r'^answer/delete/(?P<question_for>[a-z]+)/$', views.AnswerDelete.as_view(), name='delete-answer'),
    url(r'^reset/$', views.GetCategorySchemes.as_view(), name='category-funds-reset'),   ## ???
    url(r'^portfolio/change/$', views.ChangePortfolio.as_view(), name='change-portfolio'),
    url(r'^funds/distribution/validate/$', views.FundsDistributionValidate.as_view(), name='funds-distribution-validate'),
    url(r'^dashboard/v2/$', views.DashboardVersionTwo.as_view(), name='dashboard-v2'),
    url(r'^portfolio/details/v2/$', views.PortfolioDetailsVersionTwo.as_view(), name='portfolio-details-v2'),
    url(r'^portfolio/tracker/$', views.PortfolioTracker.as_view(), name='portfolio-tracker'),

    url(r'^billdesk/complete/$', views.BilldeskComplete.as_view(), name='billdesk-complete'),
    url(r'^billdesk/success/$', views.Billdesk.as_view(), name='billdesk-success'),
    url(r'^billdesk/fail/$', views.Billdesk.as_view(), name='billdesk-fail'),

    # ===================  DEPRECATED APIS =========================================================================

    url(r'^risk/profile/$', views.RiskProfile.as_view(), name='risk-profile'),
    url(r'^plan/new/response/add/$', views.PlanAnswer.as_view(), name='plan-new-answers-add'),
    url(r'^redemption/detail/$', views.TransactionDetail.as_view(), name='redemption-detail'),
    url(r'^swap/funds/$', views.SwapFunds.as_view(), name='swap-funds'),




]
