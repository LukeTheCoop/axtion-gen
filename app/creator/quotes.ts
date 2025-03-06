interface Quote {
  quote: string;
  author: string;
  category: 'inspirational' | 'scripture';
}

export const QUOTES: Quote[] = [
  // Inspirational Quotes
  {
    quote: "Life is about making an impact, not making an income.",
    author: "Kevin Kruse",
    category: "inspirational"
  },
  {
    quote: "Whatever the mind of man can conceive and believe, it can achieve.",
    author: "Napoleon Hill",
    category: "inspirational"
  },
  {
    quote: "Strive not to be a success, but rather to be of value.",
    author: "Albert Einstein",
    category: "inspirational"
  },
  {
    quote: "You miss 100% of the shots you don't take.",
    author: "Wayne Gretzky",
    category: "inspirational"
  },
  {
    quote: "I attribute my success to this: I never gave or took any excuse.",
    author: "Florence Nightingale",
    category: "inspirational"
  },
  {
    quote: "The most difficult thing is the decision to act, the rest is merely tenacity.",
    author: "Amelia Earhart",
    category: "inspirational"
  },
  {
    quote: "Every strike brings me closer to the next home run.",
    author: "Babe Ruth",
    category: "inspirational"
  },
  {
    quote: "You can never cross the ocean until you have the courage to lose sight of the shore.",
    author: "Christopher Columbus",
    category: "inspirational"
  },
  {
    quote: "The mind is everything. What you think you become.",
    author: "Buddha",
    category: "inspirational"
  },
  {
    quote: "Your time is limited, so don't waste it living someone else's life.",
    author: "Steve Jobs",
    category: "inspirational"
  },
  {
    quote: "Whether you think you can or you think you can't, you're right.",
    author: "Henry Ford",
    category: "inspirational"
  },
  {
    quote: "The best revenge is massive success.",
    author: "Frank Sinatra",
    category: "inspirational"
  },
  // Scriptures
  {
    quote: "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.",
    author: "Jeremiah 29:11",
    category: "scripture"
  },
  {
    quote: "So do not fear, for I am with you; do not be dismayed, for I am your God. I will strengthen you and help you; I will uphold you with my righteous right hand.",
    author: "Isaiah 41:10",
    category: "scripture"
  },
  {
    quote: "I can do all this through him who gives me strength.",
    author: "Philippians 4:13",
    category: "scripture"
  },
  {
    quote: "Have I not commanded you? Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.",
    author: "Joshua 1:9",
    category: "scripture"
  },
  {
    quote: "But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint.",
    author: "Isaiah 40:31",
    category: "scripture"
  },
  {
    quote: "Be on your guard; stand firm in the faith; be courageous; be strong.",
    author: "1 Corinthians 16:13",
    category: "scripture"
  },
  {
    quote: "Whatever you do, work at it with all your heart, as working for the Lord, not for human masters.",
    author: "Colossians 3:23",
    category: "scripture"
  },
  {
    quote: "In the same way, let your light shine before others, that they may see your good deeds and glorify your Father in heaven.",
    author: "Matthew 5:16",
    category: "scripture"
  }
];

// Export confetti colors for success overlay
export const CONFETTI_COLORS = ['#60A5FA', '#34D399', '#818CF8', '#C084FC', '#F472B6']; 