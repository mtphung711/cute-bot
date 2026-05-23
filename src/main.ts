import Phaser from 'phaser';

const W = 480;
const H = 320;
const SPEED = 120;
const DIRS = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW'] as const;
type Direction = (typeof DIRS)[number];

const ANGLE_DIRS: Direction[] = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'];

function dirFromVelocity(vx: number, vy: number): Direction {
  const angle = Math.atan2(-vy, vx);
  const idx = Math.round(((angle + Math.PI * 2) % (Math.PI * 2)) / (Math.PI / 4)) % 8;
  return ANGLE_DIRS[idx];
}

class RobotScene extends Phaser.Scene {
  private robot!: Phaser.Physics.Arcade.Sprite;
  private facing: Direction = 'S';
  private keys!: Record<'up' | 'down' | 'left' | 'right', Phaser.Input.Keyboard.Key>;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;

  preload() {
    this.load.spritesheet('robot', 'robot.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('egg', 'egg.png', { frameWidth: 32, frameHeight: 32 });
  }

  create() {
    const TILE = 32;
    const g = this.add.graphics();
    g.fillStyle(0x6b5d8f, 1).fillRect(0, 0, TILE, TILE);
    g.fillStyle(0x7a6ca0, 1);
    for (let i = -TILE; i < TILE * 2; i += 8) {
      g.fillRect(i, 0, 4, TILE);
    }
    g.lineStyle(1, 0x4a3f6a, 1).strokeRect(0, 0, TILE, TILE);
    g.generateTexture('ground', TILE, TILE);
    g.destroy();
    this.add.tileSprite(0, 0, W, H, 'ground').setOrigin(0, 0);

    DIRS.forEach((dir, row) => {
      this.anims.create({
        key: `robot-walk-${dir}`,
        frames: this.anims.generateFrameNumbers('robot', {
          start: row * 6,
          end: row * 6 + 5,
        }),
        frameRate: 10,
        repeat: -1,
      });
    });

    this.anims.create({
      key: 'egg-wiggle',
      frames: this.anims.generateFrameNumbers('egg', { start: 0, end: 7 }),
      frameRate: 8,
      repeat: -1,
    });
    const egg = this.add.sprite(W / 2 - 56, H / 2 + 24, 'egg', 0);
    egg.setDepth(0);
    egg.play('egg-wiggle');

    this.robot = this.physics.add.sprite(W / 2, H / 2, 'robot', 0);
    this.robot.setCollideWorldBounds(true);
    this.robot.setDepth(1);
    this.robot.play('robot-walk-S');
    this.robot.anims.pause();
    this.facing = 'S';

    this.keys = this.input.keyboard!.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.W,
      down: Phaser.Input.Keyboard.KeyCodes.S,
      left: Phaser.Input.Keyboard.KeyCodes.A,
      right: Phaser.Input.Keyboard.KeyCodes.D,
    }) as Record<'up' | 'down' | 'left' | 'right', Phaser.Input.Keyboard.Key>;
    this.cursors = this.input.keyboard!.createCursorKeys();
  }

  update() {
    const k = this.keys, c = this.cursors;
    let vx = 0, vy = 0;
    if (k.left.isDown || c.left.isDown) vx -= 1;
    if (k.right.isDown || c.right.isDown) vx += 1;
    if (k.up.isDown || c.up.isDown) vy -= 1;
    if (k.down.isDown || c.down.isDown) vy += 1;

    if (vx !== 0 || vy !== 0) {
      const len = Math.hypot(vx, vy);
      vx = (vx / len) * SPEED;
      vy = (vy / len) * SPEED;
      this.robot.setVelocity(vx, vy);

      const dir = dirFromVelocity(vx, vy);
      if (dir !== this.facing || !this.robot.anims.isPlaying) {
        this.robot.play(`robot-walk-${dir}`, true);
        this.facing = dir;
      }
    } else {
      this.robot.setVelocity(0, 0);
      if (this.robot.anims.isPlaying) {
        this.robot.anims.pause();
        const row = DIRS.indexOf(this.facing);
        this.robot.setFrame(row * 6);
      }
    }
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: W,
  height: H,
  pixelArt: true,
  roundPixels: true,
  backgroundColor: '#14171f',
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    zoom: 2,
  },
  physics: { default: 'arcade', arcade: { debug: false } },
  scene: RobotScene,
});
