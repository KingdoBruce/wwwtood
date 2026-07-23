(() => {
  const POST_PAGE_SIZE = 10;
  const TAG_PAGE_SIZE = 12;
  let postPage = 1;
  let tagPage = 1;

  function paginationMarkup(page, totalPages, totalItems, label) {
    if (totalPages <= 1) return "";
    return `<nav class="studio-pagination" aria-label="${label}">
      <button type="button" data-page="${page - 1}" ${page <= 1 ? "disabled" : ""}><span>←</span><b>上一页</b></button>
      <span><small>PAGE</small><strong>${String(page).padStart(2, "0")} / ${String(totalPages).padStart(2, "0")}</strong><em>共 ${totalItems} 条</em></span>
      <button type="button" data-page="${page + 1}" ${page >= totalPages ? "disabled" : ""}><b>下一页</b><span>→</span></button>
    </nav>`;
  }

  function bindPagination(container, onChange) {
    container.querySelectorAll("button[data-page]").forEach(button => {
      button.onclick = () => {
        onChange(Number(button.dataset.page));
        const view = container.closest(".view");
        window.scrollTo({ top: Math.max(0, view.offsetTop - 20), behavior: "smooth" });
      };
    });
  }

  function renderPostPage() {
    const totalPages = Math.max(1, Math.ceil(posts.length / POST_PAGE_SIZE));
    postPage = Math.min(Math.max(1, postPage), totalPages);
    const start = (postPage - 1) * POST_PAGE_SIZE;
    const pagePosts = posts.slice(start, start + POST_PAGE_SIZE);
    document.getElementById("postList").innerHTML = pagePosts.map((post, index) => `
      <article class="post-row" data-slug="${escapeHtml(post.slug)}">
        <code>A.${String(start + index + 1).padStart(3, "0")}</code>
        <div>
          <strong>${escapeHtml(post.title)}</strong>
          <button type="button" class="text-button delete-post-row" data-slug="${escapeHtml(post.slug)}" data-title="${escapeHtml(post.title)}">删除</button>
          <p>${escapeHtml(post.description || post.slug)}</p>
        </div>
        <span>${escapeHtml((post.categories || []).join(" / ") || "未分类")}</span>
        <time>${escapeHtml(fmtDate(post.date))}</time>
        <span class="badge ${post.draft ? "draft" : ""}">${post.draft ? "草稿" : "已发布"}</span>
      </article>
    `).join("") || '<div class="empty">点击“新建文章”开始写作</div>';

    const pagination = document.getElementById("postPagination");
    pagination.innerHTML = paginationMarkup(postPage, totalPages, posts.length, "文章管理分页");
    bindPagination(pagination, page => {
      postPage = page;
      renderPostPage();
    });

    document.querySelectorAll(".post-row").forEach(row => {
      row.onclick = event => {
        if (!event.target.closest(".delete-post-row")) editPost(row.dataset.slug);
      };
    });
    document.querySelectorAll(".delete-post-row").forEach(button => {
      button.onclick = event => {
        event.stopPropagation();
        deletePostBySlug(button.dataset.slug, button.dataset.title);
      };
    });
  }

  loadPosts = async function () {
    try {
      posts = (await api("/api/posts")).posts;
      renderPostPage();
    } catch (error) {
      notice(error.message, true);
    }
  };

  renderTaxonomy = function (kind) {
    const singular = kind === "categories" ? "分类" : "标签";
    const list = document.getElementById(kind === "categories" ? "categoryList" : "tagList");
    const total = document.getElementById(kind === "categories" ? "categoryTotal" : "tagTotal");
    const items = taxonomyData[kind] || [];
    let visibleItems = items;

    if (kind === "tags") {
      const totalPages = Math.max(1, Math.ceil(items.length / TAG_PAGE_SIZE));
      tagPage = Math.min(Math.max(1, tagPage), totalPages);
      const start = (tagPage - 1) * TAG_PAGE_SIZE;
      visibleItems = items.slice(start, start + TAG_PAGE_SIZE);
      const pagination = document.getElementById("tagPagination");
      pagination.innerHTML = paginationMarkup(tagPage, totalPages, items.length, "标签管理分页");
      bindPagination(pagination, page => {
        tagPage = page;
        renderTaxonomy("tags");
      });
    }

    total.textContent = items.length;
    list.innerHTML = visibleItems.map(item => `
      <div class="taxonomy-row${kind === "categories" ? " has-visibility" : ""}">
        <strong>${escapeHtml(item.name)}</strong>
        <small>${item.count} 篇文章</small>
        ${kind === "categories" ? `<div class="taxonomy-visibility">
          <label><span>首页显示</span><input class="category-display-toggle" type="checkbox" data-name="${encodeURIComponent(item.name)}" data-field="show_on_home" ${item.show_on_home !== false ? "checked" : ""}></label>
          <label><span>归档分类索引</span><input class="category-display-toggle" type="checkbox" data-name="${encodeURIComponent(item.name)}" data-field="show_in_archives" ${item.show_in_archives !== false ? "checked" : ""}></label>
        </div>` : ""}
        <div class="taxonomy-actions">
          <button class="button ghost rename-taxonomy" data-kind="${kind}" data-name="${encodeURIComponent(item.name)}">重命名</button>
          <button class="button ghost delete-taxonomy" data-kind="${kind}" data-name="${encodeURIComponent(item.name)}">删除</button>
        </div>
      </div>
    `).join("") || `<div class="empty">还没有${singular}</div>`;

    list.querySelectorAll(".category-display-toggle").forEach(input => {
      input.onchange = () => saveCategoryDisplay(input);
    });
    list.querySelectorAll(".rename-taxonomy").forEach(button => {
      button.onclick = () => renameTaxonomy(button.dataset.kind, decodeURIComponent(button.dataset.name));
    });
    list.querySelectorAll(".delete-taxonomy").forEach(button => {
      button.onclick = () => deleteTaxonomy(button.dataset.kind, decodeURIComponent(button.dataset.name));
    });
  };
})();
