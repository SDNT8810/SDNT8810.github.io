# Davoud Nikkhouy - Portfolio Website

A modern, responsive React portfolio website showcasing expertise in robotics, embedded systems, and AI-driven control.

## Features

- **Modular Design**: Easy to update and maintain with centralized content management
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- **Project Showcase**: Support for images and YouTube videos in project pages
- **Dynamic Routing**: Individual pages for each project (e.g., `/projects/bilevel-mpc`)
- **Professional Sections**: Home, Experience, Education, Skills, Publications, and Projects

## Project Structure

```
portfolio-website/
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Main layout with navigation
│   │   └── ui/                 # UI components (shadcn/ui)
│   ├── pages/
│   │   ├── Home.jsx            # Homepage
│   │   ├── Experience.jsx      # Work experience
│   │   ├── Education.jsx       # Education background
│   │   ├── Skills.jsx          # Technical skills
│   │   ├── Publications.jsx    # Research publications
│   │   ├── Projects.jsx        # Projects overview
│   │   └── ProjectDetail.jsx   # Individual project pages
│   ├── data/
│   │   └── content.js          # Centralized content management
│   ├── assets/                 # Images and static files
│   └── App.jsx                 # Main app with routing
├── dist/                       # Production build files
└── public/                     # Public assets
```

## Content Management

All content is managed through the `src/data/content.js` file. This makes it easy to:

- Update personal information
- Add new work experiences
- Add new projects
- Update skills and technologies
- Add new publications

### Adding New Projects

1. Open `src/data/content.js`
2. Add a new project object to the `projects` array:

```javascript
{
  id: "your-project-id",
  title: "Your Project Title",
  shortDescription: "Brief description",
  description: "Detailed description",
  technologies: ["Tech1", "Tech2", "Tech3"],
  images: ["/src/assets/your-image.jpg"],
  youtubeVideos: ["VIDEO_ID_HERE"],
  githubUrl: "https://github.com/...",
  demoUrl: "https://...",
  featured: true // or false
}
```

3. The project will automatically appear in the projects list and be accessible at `/projects/your-project-id`

### Adding Images

1. Copy your images to the `src/assets/` directory
2. Reference them in the content file using the path: `/src/assets/your-image.jpg`

### Adding YouTube Videos

1. Get the video ID from your YouTube URL (e.g., from `https://youtube.com/watch?v=ABC123`, use `"ABC123"`)
2. Add the video ID to the `youtubeVideos` array in your project

## Development

### Prerequisites

- Node.js (v20 or higher)
- pnpm package manager

### Setup

1. Install dependencies:
```bash
pnpm install
```

2. Start development server:
```bash
pnpm run dev
```

3. Build for production:
```bash
pnpm run build
```

## Deployment to GitHub Pages

### Option 1: Manual Deployment

1. Build the project:
```bash
pnpm run build
```

2. Copy all files from the `dist/` folder to your `SDNT8810.github.io` repository

3. Commit and push to GitHub:
```bash
git add .
git commit -m "Update portfolio website"
git push origin main
```

### Option 2: Automated Deployment with GitHub Actions

Create `.github/workflows/deploy.yml` in your `SDNT8810.github.io` repository:

```yaml
name: Deploy Portfolio

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '20'
        
    - name: Install pnpm
      run: npm install -g pnpm
        
    - name: Install dependencies
      run: pnpm install
      
    - name: Build
      run: pnpm run build
      
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
```

## Custom Domain Setup (davoudnikkhouy.com)

1. In your GitHub repository settings, go to "Pages"
2. Under "Custom domain", enter: `davoudnikkhouy.com`
3. Enable "Enforce HTTPS"
4. In your domain registrar's DNS settings, add these records:

```
Type: A
Name: @
Value: 185.199.108.153

Type: A
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153

Type: CNAME
Name: www
Value: sdnt8810.github.io
```

5. Create a `CNAME` file in your repository root with content: `davoudnikkhouy.com`

## Technologies Used

- **React 18** - Frontend framework
- **Vite** - Build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI components
- **Lucide React** - Icon library
- **React Router** - Client-side routing
- **Framer Motion** - Animation library

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

The website is optimized for performance with:
- Code splitting
- Lazy loading
- Optimized images
- Minimal bundle size
- Fast loading times

## Maintenance

To keep the website updated:

1. Regularly update the content in `src/data/content.js`
2. Add new project images to `src/assets/`
3. Update dependencies periodically:
```bash
pnpm update
```

## Support

For any issues or questions about the website, please refer to:
- React documentation: https://react.dev/
- Tailwind CSS documentation: https://tailwindcss.com/
- shadcn/ui documentation: https://ui.shadcn.com/

## License

This project is for personal use. Feel free to use it as inspiration for your own portfolio website.

